"""Shared CrewAI bootstrap and default LLM (Anthropic API or Claude Code CLI)."""

import os
from pathlib import Path

from crewai import LLM
from crewai.llms.base_llm import BaseLLM

from arvo_auth_orchestrator.claude_code_llm import ClaudeCodeLLM
from arvo_auth_orchestrator.crewai_react_parse_fix import apply_crewai_react_final_answer_fix


def _bootstrap_project_local_home_for_crewai_sqlite() -> None:
    """See README: ARVO_CREWAI_IN_PROJECT_HOME for CI / restricted HOME."""
    if os.getenv("ARVO_CREWAI_IN_PROJECT_HOME", "").strip() != "1":
        return
    root = Path(__file__).resolve().parents[2]
    fake_home = root / ".crewai_runtime_home"
    fake_home.mkdir(parents=True, exist_ok=True)
    os.environ["HOME"] = str(fake_home)


_bootstrap_project_local_home_for_crewai_sqlite()


def _resolve_llm_backend() -> str:
    """Return ``anthropic`` (CrewAI + API) or ``claude_code`` (``claude -p``)."""
    raw = os.getenv("ARVO_LLM_BACKEND", "").strip().lower()
    if raw in ("anthropic", "api"):
        return "anthropic"
    if raw in ("claude_code", "claude-code", "cli", "code"):
        return "claude_code"
    if raw:
        return "anthropic"
    if os.getenv("ANTHROPIC_API_KEY", "").strip():
        return "anthropic"
    return "claude_code"


def default_llm() -> BaseLLM:
    if _resolve_llm_backend() == "claude_code":
        label = os.getenv("ARVO_CLAUDE_CODE_MODEL_LABEL", "claude-code-cli").strip()
        return ClaudeCodeLLM(model=label or "claude-code-cli")
    model = os.getenv("MODEL", "anthropic/claude-sonnet-4-20250514").strip()
    max_tokens = int(os.getenv("ANTHROPIC_MAX_TOKENS", "8192"))
    return LLM(model=model, max_tokens=max_tokens)


apply_crewai_react_final_answer_fix()
