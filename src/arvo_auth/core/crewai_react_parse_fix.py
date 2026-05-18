"""Patch CrewAI ReAct parsing so ``Task.output_file`` receives the full final document.

CrewAI's default ``parse()`` sets ``AgentFinish.output`` to
``text.split('Final Answer:')[-1]``. Any markdown that contains that substring again
(e.g. UI copy, embedded ReAct examples) loses everything before the *last* occurrence.

We also prefer extracting after the first structured delimiter (``\\nFinal Answer:\\n``)
when the model follows the template, avoiding accidental mid-body matches when possible.
"""

from __future__ import annotations

import logging
import re

from crewai.agents.constants import FINAL_ANSWER_ACTION
from crewai.agents.parser import AgentAction, AgentFinish

logger = logging.getLogger(__name__)

_applied = False

_FINAL_MARKERS: tuple[str, ...] = (
    "\n\nFinal Answer:\n",
    "\nFinal Answer:\n",
    "\nFinal Answer:",
    "Final Answer:\n",
)


def _trim_trailing_odd_fence(final_answer: str) -> str:
    """Match crewai.agents.parser.parse trailing ``` handling."""
    if final_answer.endswith("```"):
        count = final_answer.count("```")
        if count % 2 != 0:
            return final_answer[:-3].rstrip()
    return final_answer


def _extract_after_first_final_marker(raw: str) -> str | None:
    """Return body after the first ReAct-style ``Final Answer`` line, if found."""
    for marker in _FINAL_MARKERS:
        if marker in raw:
            return raw.split(marker, 1)[1].strip()
    m = re.search(r"(?ms)^\s*Final Answer:\s*", raw)
    if m:
        return raw[m.end() :].strip()
    return None


def _restore_final_answer_output(result: AgentAction | AgentFinish) -> AgentAction | AgentFinish:
    if isinstance(result, AgentAction):
        return result
    if not isinstance(result, AgentFinish):
        return result
    if not isinstance(result.output, str) or not isinstance(result.text, str):
        return result
    full = result.text
    if FINAL_ANSWER_ACTION not in full:
        return result

    pieces = full.split(FINAL_ANSWER_ACTION)
    if len(pieces) > 2:
        fixed = FINAL_ANSWER_ACTION.join(pieces[1:]).strip()
    else:
        ext = _extract_after_first_final_marker(full)
        fixed = ext if ext is not None else result.output

    fixed = _trim_trailing_odd_fence(fixed.strip())

    if fixed != result.output:
        logger.debug(
            "crewai_react_parse_fix: adjusted Final Answer body (%d -> %d chars)",
            len(result.output),
            len(fixed),
        )
    return AgentFinish(thought=result.thought, output=fixed, text=result.text)


def apply_crewai_react_final_answer_fix() -> None:
    """Idempotent monkey-patch of ``crewai.agents.parser.parse``."""
    global _applied
    if _applied:
        return
    import crewai.agents.parser as parser_module

    original = parser_module.parse

    def parse_wrapped(text: str) -> AgentAction | AgentFinish:
        return _restore_final_answer_output(original(text))

    parse_wrapped.__name__ = "parse"
    parse_wrapped.__doc__ = original.__doc__
    parser_module.parse = parse_wrapped  # type: ignore[method-assign]
    _applied = True
