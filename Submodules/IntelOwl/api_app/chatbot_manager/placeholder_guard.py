# This file is a part of IntelOwl https://github.com/intelowlproject/IntelOwl
# See the file 'LICENSE' for copying permission.

"""Post-generation guard against fabricated bracketed names in a chat answer.

The system prompt tells the model to copy analyzer, playbook and job names verbatim from tool
results and never emit bracketed labels like ``[Analyzer 1]``. A rule that lives only in the prompt
is probabilistic by construction: measured answers show the model can still invent a whole section
(typically a playbook list) and, having no names to copy, fill it with placeholders. This module is
the deterministic backstop, and it never calls the LLM.

It detects and annotates; it deliberately does not repair. In the observed failures the tool payload
carried no playbook data at all, so there is no real name to substitute, and rewriting would mean a
second inference on a local CPU-bound model — a plain retry would not even change the answer, since
the agent runs at temperature 0.

Precision is preferred over coverage: a false positive would stamp a warning onto a correct answer,
which is worse than missing a rare shape. The criterion is therefore anchored to the entity nouns
the prompt rule protects, and the prompt rule remains the first line of defense for the shapes this
misses (``[X]``, ``[TBD]``, ``[insert name]``).
"""

import logging
import re

logger = logging.getLogger(__name__)

# What the notice claims is exactly what the criterion below checks: a bracketed span *shaped* like
# a name slot. The guard never inspects the tool results, so it cannot assert the name is ungrounded
# — only that it does not look like a real IntelOwl name.
PLACEHOLDER_NOTICE = (
    "_Note: this answer contains bracketed names that look like placeholders rather than real "
    "IntelOwl names. Treat them as unverified._"
)
_NOTICE_SEPARATOR = "\n\n"

# Every notice wording ever persisted, newest first. `strip_notice` has to recognize all of them,
# not just the current one: assistant rows written by an earlier version stay in the database and
# are replayed into the prompt on the next turn, so rewording the notice without this would
# silently start leaking it back into the model's context with no test failing.
# APPEND a new wording here when PLACEHOLDER_NOTICE changes; never edit or drop an entry.
_HISTORICAL_NOTICES = (PLACEHOLDER_NOTICE,)

# A candidate is a single-line `[...]` span NOT followed by "(": that lookahead excludes markdown
# links `[text](url)`, which the chat panel renders as real anchors. The length bound keeps a
# candidate at name-slot size (the longest occurrence measured is 46 characters) so bracketed prose
# is not a candidate at all.
_MAX_PLACEHOLDER_LEN = 80
_CANDIDATE_RE = re.compile(rf"\[([^\[\]\n]{{1,{_MAX_PLACEHOLDER_LEN}}})\](?!\()")

# A candidate is a placeholder only when it STARTS with one of the entity nouns the prompt rule
# protects. The start anchor is what keeps out defanged indicators (`example[.]com`), footnote
# markers (`[1]`), GFM task-list boxes (`- [x]`) and JSON echoes of a tool result.
#
# This list is the Python side of the rule stated in `agent/system_prompt.txt` ([Rules], the "Copy
# analyzer, playbook and job names verbatim" line). The prompt file carries no reciprocal comment on
# purpose — it is sent to the model verbatim, so a note to maintainers would become prompt tokens;
# the coupling is pinned from this side instead, by a test that derives the rule's own examples from
# the prompt text. The two lists are deliberately not identical: the prompt names three nouns, while
# a detector can afford two more, because widening a regex cannot degrade generation, whereas
# widening the prompt spends context budget and forces the narration gate to be re-measured.
_ENTITY_RE = re.compile(r"^(analyzer|playbook|job|investigation|observable)s?\b", re.IGNORECASE)


def find_placeholders(text: str) -> list[str]:
    """Return the bracketed placeholder spans in ``text``, brackets included, in order."""
    return [
        match.group(0) for match in _CANDIDATE_RE.finditer(text) if _ENTITY_RE.match(match.group(1).strip())
    ]


def guard_answer(text: str, *, session_id: int) -> str:
    """Annotate ``text`` when it names entities no tool result provided; return it unchanged if not.

    The model's prose is never edited: removing the spans would leave empty list bullets and an
    orphan lead-in. One notice is appended however many spans matched, because the annotation is a
    statement about the answer, not about each occurrence. The notice is appended unconditionally,
    so an answer that ends inside an unterminated code fence renders it as code; closing the fence
    would mean editing the model's output, which this guard exists not to do.

    The warning is the only telemetry this has (IntelOwl has no metrics pipeline for the chatbot),
    so the message prefix is kept stable and greppable to count the real production frequency.
    """
    placeholders = find_placeholders(text)
    if not placeholders:
        return text
    logger.warning("chatbot placeholder guard: session=%s placeholders=%s", session_id, placeholders)
    return f"{text}{_NOTICE_SEPARATOR}{PLACEHOLDER_NOTICE}"


def strip_notice(text: str) -> str:
    """Remove a notice previously appended by ``guard_answer``, in any wording ever shipped.

    Only a *trailing* notice is removed: anything else in the text is the model's own output and
    must survive verbatim.
    """
    for notice in _HISTORICAL_NOTICES:
        stripped = text.removesuffix(f"{_NOTICE_SEPARATOR}{notice}")
        if stripped != text:
            return stripped
    return text
