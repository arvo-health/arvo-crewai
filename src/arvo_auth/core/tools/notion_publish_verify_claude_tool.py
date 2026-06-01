"""Post-publish completeness audit: SRS vs Notion via Claude Code CLI (MCP)."""

from __future__ import annotations

import os
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from arvo_auth.core.srs_notion_publish_config import (
    ENGINEERING_NOTION_PUBLISH,
    SrsNotionPublishTeamConfig,
)
from arvo_auth.core.srs_publish_paths import (
    publish_execution_log_path,
    publish_plan_path,
    resolve_srs_publish_path,
)
from arvo_auth.core.tools.notion_claude_delegate import run_claude_code_print


class NotionPublishVerifyInput(BaseModel):
    """Unused; the tool reads artefacts from disk."""

    unused: str = Field(default="", description="Leave empty.")


class NotionPublishVerifyViaClaudeTool(BaseTool):
    name: str = "notion_verify_srs_publish_completeness_via_claude"
    description: str = (
        "After notion_publish_srs_via_claude: run one Claude Code subprocess with Notion MCP "
        "to compare the full SRS.md on disk against the created Notion pages, list any missing "
        "content, and patch Notion via MCP. Reads publish_plan.md and publish_execution_log.md "
        "from the team's notion_export folder. Timeout: NOTION_PUBLISH_VERIFY_CLAUDE_TIMEOUT_SEC "
        "(default 3600)."
    )
    args_schema: Type[BaseModel] = NotionPublishVerifyInput
    publish_config: SrsNotionPublishTeamConfig = ENGINEERING_NOTION_PUBLISH

    def _run(self, unused: str = "") -> str:
        cfg = self.publish_config
        srs_path, err = resolve_srs_publish_path(cfg)
        if err:
            return err
        assert srs_path is not None

        parent_ref, parent_err = cfg.resolve_notion_parent()
        if parent_err or not parent_ref:
            return parent_err or (
                f"Set {cfg.notion_parent_url_env} (full Notion page URL) or legacy "
                f"{cfg.notion_parent_id_env} for the completeness audit."
            )

        plan_file = publish_plan_path(cfg)
        log_file = publish_execution_log_path(cfg)
        plan_excerpt = ""
        if plan_file.is_file():
            raw = plan_file.read_text(encoding="utf-8", errors="replace")
            plan_excerpt = raw[:40_000]
            if len(raw) > 40_000:
                plan_excerpt += (
                    "\n\n[... publish_plan.md truncated in prompt; read full file from disk ...]\n"
                )
        else:
            plan_excerpt = "(publish_plan.md not found on disk.)"

        log_excerpt = ""
        if log_file.is_file():
            raw = log_file.read_text(encoding="utf-8", errors="replace")
            log_excerpt = raw[:60_000]
            if len(raw) > 60_000:
                log_excerpt += (
                    "\n\n[... publish_execution_log.md truncated in prompt; "
                    "read full file from disk ...]\n"
                )
        else:
            log_excerpt = "(publish_execution_log.md not found — run publish step first.)"

        parent_hint = parent_ref.prompt_hint()

        timeout = int(os.getenv("NOTION_PUBLISH_VERIFY_CLAUDE_TIMEOUT_SEC", "3600"))

        prompt = f"""You are the Notion Architect completing a **lossless publish audit** for an SRS. You have Notion MCP (same as interactive Claude Code).

## Source of truth (read the ENTIRE file with your Read tool — do not rely only on excerpts)
Absolute path: {srs_path}

## On-disk artefacts (read full files if the excerpts below are truncated)
- Plan: {plan_file}
- Execution log (page titles / URLs): {log_file}

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
