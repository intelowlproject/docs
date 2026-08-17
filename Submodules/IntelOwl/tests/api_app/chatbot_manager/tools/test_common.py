# This file is a part of IntelOwl https://github.com/intelowlproject/IntelOwl
# See the file 'LICENSE' for copying permission.

from django.test import TestCase

from api_app.chatbot_manager.agent.tools._common import MAX_RESULTS, clamp_limit


class ClampLimitHelperTestCase(TestCase):
    """Unit tests for the shared `clamp_limit` helper used by the analyzer/playbook tools."""

    def test_within_range_passes_through(self):
        errors = []
        self.assertEqual(clamp_limit(10, errors), 10)
        self.assertEqual(errors, [])

    def test_over_cap_clamps_and_warns(self):
        errors = []
        self.assertEqual(clamp_limit(999, errors), MAX_RESULTS)
        self.assertTrue(any("exceeds the maximum" in e for e in errors))

    def test_below_one_clamps_up_silently(self):
        # A non-positive limit is bounded up to 1 without a warning (only over-cap is worth one).
        errors = []
        self.assertEqual(clamp_limit(0, errors), 1)
        self.assertEqual(clamp_limit(-5, errors), 1)
        self.assertEqual(errors, [])
