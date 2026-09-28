# This file is a part of IntelOwl https://github.com/intelowlproject/IntelOwl
# See the file 'LICENSE' for copying permission.

import re
from unittest.mock import patch

from django.test import SimpleTestCase

from api_app.chatbot_manager.agent.agent import _SYSTEM_PROMPT
from api_app.chatbot_manager.placeholder_guard import (
    _MAX_PLACEHOLDER_LEN,
    PLACEHOLDER_NOTICE,
    find_placeholders,
    guard_answer,
    strip_notice,
)

SESSION_ID = 11


class FindPlaceholdersTestCase(SimpleTestCase):
    """The detector fires on fabricated bracketed names — and on nothing else.

    The two detection cases are answers actually recorded during the 2026-08-03 narration
    measurement, kept verbatim so a future change to the criterion is measured against real model
    output rather than against invented examples.
    """

    def test_detects_a_bracketed_list_of_invented_playbooks(self):
        text = (
            "The playbooks that can analyze this type of observable are:\n\n"
            "- [Playbook X]  \n"
            "- [Playbook Y]\n"
        )
        self.assertEqual(find_placeholders(text), ["[Playbook X]", "[Playbook Y]"])

    def test_detects_a_whole_sentence_used_as_a_name_slot(self):
        # The failure is not always shaped like [Label N]: a detector tuned on that shape alone
        # would miss this one, which was recorded in the same campaign.
        text = (
            "This analysis is based on the following playbook(s): "
            "[Playbook names will be listed here if available]."
        )
        self.assertEqual(find_placeholders(text), ["[Playbook names will be listed here if available]"])

    def test_detects_every_example_the_prompt_rule_itself_names(self):
        # Coupling test: the guard is the deterministic half of a rule whose canonical wording lives
        # in system_prompt.txt. Deriving the examples from the prompt instead of hardcoding them
        # means rewording that rule breaks this test loudly, rather than leaving the guard silently
        # out of step with the instruction it backs up.
        rule_lines = [line for line in _SYSTEM_PROMPT.splitlines() if "bracketed labels" in line]
        self.assertEqual(len(rule_lines), 1, "the anti-placeholder rule is no longer in the prompt")
        examples = re.findall(r"\[[^\[\]\n]+\]", rule_lines[0])
        self.assertTrue(examples, "the rule no longer shows bracketed examples")
        self.assertEqual(find_placeholders(" and ".join(examples)), examples)

    def test_ignores_markdown_links(self):
        # The chat panel renders links as real anchors (chatMarkdown.jsx), so this is live output.
        text = "Supported by [AILTypoSquatting](https://intelowl.example/analyzer/1)."
        self.assertEqual(find_placeholders(text), [])

    def test_ignores_defanged_indicators(self):
        text = "Observable example[.]com resolved to 1.1.1[.]1 over hxxp[:]//example[.]com."
        self.assertEqual(find_placeholders(text), [])

    def test_ignores_gfm_task_list_boxes(self):
        self.assertEqual(find_placeholders("- [x] done\n- [ ] pending\n"), [])

    def test_ignores_footnote_markers_and_json_echoes_of_tool_output(self):
        text = 'Silent analyzers [1]: ["AbuseIPDB", "Abusix"]'
        self.assertEqual(find_placeholders(text), [])

    def test_ignores_the_prompt_section_headers(self):
        self.assertEqual(find_placeholders("[Rules] and [Response style] are prompt sections."), [])

    def test_ignores_a_span_too_long_to_be_a_name_slot(self):
        # Prose in brackets is not a name placeholder; the length bound keeps the criterion narrow.
        self.assertEqual(find_placeholders(f"text [job {'x' * 90}] more"), [])

    def test_the_length_bound_is_inclusive_at_the_boundary(self):
        # The decision the bound encodes is only exercised at the boundary itself, not 90 chars past
        # it: one character either side must land on opposite sides of the criterion.
        at_limit = "job " + "x" * (_MAX_PLACEHOLDER_LEN - len("job "))
        over_limit = f"{at_limit}x"
        self.assertEqual(find_placeholders(f"text [{at_limit}] more"), [f"[{at_limit}]"])
        self.assertEqual(find_placeholders(f"text [{over_limit}] more"), [])


class GuardAnswerTestCase(SimpleTestCase):
    """A flagged answer is annotated, never edited; a clean answer is untouched and silent."""

    def test_clean_answer_is_returned_byte_for_byte(self):
        text = "Job #42 is malicious (reliability 7/10), supported by AILTypoSquatting."
        self.assertEqual(guard_answer(text, session_id=SESSION_ID), text)

    def test_flagged_answer_keeps_the_model_prose_and_gains_one_notice(self):
        text = "- [Playbook X]\n- [Playbook Y]"
        guarded = guard_answer(text, session_id=SESSION_ID)
        self.assertTrue(guarded.startswith(text))
        self.assertEqual(guarded.count(PLACEHOLDER_NOTICE), 1)

    def test_detection_is_logged_with_the_session_and_the_spans(self):
        with patch("api_app.chatbot_manager.placeholder_guard.logger.warning") as mock_warning:
            guard_answer("Use [Playbook X].", session_id=SESSION_ID)
        mock_warning.assert_called_once()
        args = mock_warning.call_args[0]
        self.assertIn("session=%s", args[0])
        self.assertEqual(args[1], SESSION_ID)
        self.assertEqual(args[2], ["[Playbook X]"])

    def test_clean_answer_logs_nothing(self):
        with patch("api_app.chatbot_manager.placeholder_guard.logger.warning") as mock_warning:
            guard_answer("Job #42 is malicious.", session_id=SESSION_ID)
        mock_warning.assert_not_called()


class StripNoticeTestCase(SimpleTestCase):
    """The notice is an annotation for the user, so it must be removable exactly."""

    def test_strip_reverses_guard(self):
        text = "Use [Playbook X]."
        self.assertEqual(strip_notice(guard_answer(text, session_id=SESSION_ID)), text)

    def test_answer_without_a_notice_is_unchanged(self):
        text = "Job #42 is malicious."
        self.assertEqual(strip_notice(text), text)

    def test_only_a_trailing_notice_is_stripped(self):
        # Anything not at the end is the model's own text and must survive verbatim.
        text = f"{PLACEHOLDER_NOTICE} and then more prose"
        self.assertEqual(strip_notice(text), text)
