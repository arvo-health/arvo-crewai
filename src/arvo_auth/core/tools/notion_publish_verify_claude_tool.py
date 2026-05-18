"""Post-publish completeness audit: SRS vs Notion via Claude Code CLI (MCP)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from arvo_auth.core.tools.notion_claude_delegate import run_claude_code_print
from arvo_auth.core.tools.srs_publish_read_tool import _resolve_srs_path


def _project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _publish_plan_path() -> Path:
    return _project_root() / "outputs" / "engineering" / "notion_export" / "publish_plan.md"


def _publish_execution_log_path() -> Path:
    return _project_root() / "outputs" / "engineering" / "notion_export" / "publish_execution_log.md"


class NotionPublishVerifyInput(BaseModel):
    """Unused; the tool reads artefacts from disk."""

    unused: str = Field(default="", description="Leave empty.")


class NotionPublishVerifyViaClaudeTool(BaseTool):
    name: str = "notion_verify_srs_publish_completeness_via_claude"
    description: str = (
        "After notion_publish_srs_via_claude: run one Claude Code subprocess with Notion MCP "
        "to compare the full SRS.md on disk against the created Notion pages, list any missing "
        "content, and patch Notion via MCP so no SRS material is omitted. Reads "
        "outputs/notion_export/publish_plan.md and publish_execution_log.md from disk. "
        "Requires NOTION_SRS_PARENT_PAGE_ID or NOTION_SRS_PARENT_URL. Timeout: "
        "NOTION_PUBLISH_VERIFY_CLAUDE_TIMEOUT_SEC (default 3600)."
    )
    args_schema: Type[BaseModel] = NotionPublishVerifyInput

    def _run(self, unused: str = "") -> str:
        srs_path, err = _resolve_srs_path()
        if err:
            return err
        assert srs_path is not None

        parent_id = os.getenv("NOTION_SRS_PARENT_PAGE_ID", "").strip()
        parent_url = os.getenv("NOTION_SRS_PARENT_URL", "").strip()
        if not parent_id and not parent_url:
            return (
                "Set NOTION_SRS_PARENT_PAGE_ID (Notion page UUID) or NOTION_SRS_PARENT_URL "
                "for the completeness audit."
            )

        plan_file = _publish_plan_path()
        log_file = _publish_execution_log_path()
        plan_excerpt = ""
        if plan_file.is_file():
            raw = plan_file.read_text(encoding="utf-8", errors="replace")
            plan_excerpt = raw[:40_000]
            if len(raw) > 40_000:
                plan_excerpt += "\n\n[... publish_plan.md truncated in prompt; read full file from disk ...]\n"
        else:
            plan_excerpt = "(publish_plan.md not found on disk.)"

        log_excerpt = ""
        if log_file.is_file():
            raw = log_file.read_text(encoding="utf-8", errors="replace")
            log_excerpt = raw[:60_000]
            if len(raw) > 60_000:
                log_excerpt += "\n\n[... publish_execution_log.md truncated in prompt; read full file from disk ...]\n"
        else:
            log_excerpt = "(publish_execution_log.md not found — run publish step first.)"

        parent_hint = (
            f"Root parent page UUID: {parent_id}" if parent_id else f"Root parent page URL: {parent_url}"
        )

        timeout = int(os.getenv("NOTION_PUBLISH_VERIFY_CLAUDE_TIMEOUT_SEC", "3600"))

        prompt = f"""You are the Notion Architect completing a **lossless publish audit** for an SRS. You have Notion MCP (same as interactive Claude Code).

## Source of truth (read the ENTIRE file with your Read tool — do not rely only on excerpts)
Absolute path: {srs_path}

## On-disk artefacts (read full files if the excerpts below are truncated)
- Plan: {_publish_plan_path()}
- Execution log (page titles / URLs): {_publish_execution_log_path()}

## Parent hint
{parent_hint}

## Excerpt — publish plan (first ~40k chars)
{plan_excerpt}

## Excerpt — execution log (first ~60k chars)
{log_excerpt}

## Mandatory audit procedure
1. Read the **complete** SRS markdown from disk. Build an internal checklist of **every** deliverable slice: each major heading (`#` through `####` as present), every markdown **table** (header row + body), every **numbered or bulleted list** under requirements (including every `RF-`, `RNF-`, `REQ-` line), every **fenced code block**, and standalone paragraphs that are not empty.
2. Using the execution log URLs (and Notion MCP navigation from the root parent if needed), open **each** created Notion page and compare against the SRS slice that should live there per the publish plan. **Summaries that omit paragraphs, tables, or list items are failures.**
3. For every gap (missing heading, missing table row, missing list item, truncated fence, missing paragraph text): **repair via Notion MCP** by appending or editing blocks so the Notion page contains the **full** corresponding SRS text (faithful markdown semantics). If a single page would exceed practical size, create a clearly named continuation child page (e.g. same section number + " (continued)") and place overflow there; link from the first part.
4. Do **not** invent requirements or URLs not in the SRS. Do not delete correctly published content unless you must replace a mistaken summary with the full source text.

## Output (plain text for the orchestrator)
First line exactly one of: `COMPLETE_OK`, `COMPLETE_GAPS_FIXED`, or `COMPLETE_FAILED`.
Then markdown bullets: for each discrepancy — SRS anchor (heading or line range), Notion page URL, what was missing, what MCP action fixed it. If `COMPLETE_FAILED`, explain blockers (e.g. MCP read denied).
"""

        return run_claude_code_print(prompt, timeout_sec=timeout)
