"""Publish the full SRS workspace to Notion via Claude Code CLI (MCP), no REST API."""

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


class NotionPublishViaClaudeInput(BaseModel):
    """Optional pasted publish plan; if empty, reads outputs/notion_export/publish_plan.md from disk."""

    publish_plan_markdown: str = Field(
        default="",
        description="Paste the publish plan from the previous task, or leave empty to read publish_plan.md from disk.",
    )


class NotionPublishViaClaudeTool(BaseTool):
    name: str = "notion_publish_srs_via_claude"
    description: str = (
        "Create the full Notion hierarchy for the SRS using the local Claude Code CLI and "
        "your Notion MCP (no NOTION_API_KEY). Run once after planning. Requires "
        "NOTION_SRS_PARENT_PAGE_ID (UUID) or NOTION_SRS_PARENT_URL. Reads SRS from disk "
        "(ARVO_SRS_PUBLISH_INPUT or default). Structure: Dashboard + one child page per SRS "
        "TOC section, preserve numbering and citation URLs. Use read_srs_for_notion_publish first if you "
        "need to verify content; this tool re-reads the file path internally."
    )
    args_schema: Type[BaseModel] = NotionPublishViaClaudeInput

    def _run(self, publish_plan_markdown: str = "") -> str:
        srs_path, err = _resolve_srs_path()
        if err:
            return err
        assert srs_path is not None

        parent_id = os.getenv("NOTION_SRS_PARENT_PAGE_ID", "").strip()
        parent_url = os.getenv("NOTION_SRS_PARENT_URL", "").strip()
        if not parent_id and not parent_url:
            return (
                "Set NOTION_SRS_PARENT_PAGE_ID (Notion page UUID) or NOTION_SRS_PARENT_URL "
                "so Claude knows where to attach new pages."
            )

        plan_text = publish_plan_markdown.strip()
        if not plan_text:
            plan_file = _publish_plan_path()
            if plan_file.is_file():
                plan_text = plan_file.read_text(encoding="utf-8", errors="replace")
            else:
                plan_text = (
                    "(No publish_plan.md on disk yet — use TOC-driven hierarchy: Dashboard under "
                    "root, then one child page per SRS table-of-contents section in order; preserve "
                    "section numbers in titles; add links for citation URLs from the SRS; preserve "
                    "RF-/RNF-/REQ- identifiers.)"
                )

        parent_hint = (
            f"Parent page UUID: {parent_id}" if parent_id else f"Parent page URL: {parent_url}"
        )

        timeout = int(os.getenv("NOTION_PUBLISH_CLAUDE_TIMEOUT_SEC", "1800"))

        prompt = f"""You are the Notion Architect for Software Engineering. You have Notion MCP (same as interactive Claude Code).

## Task
Create a structured Notion workspace under the user's **root** parent page that reflects the SRS.

## Parent (attach all new pages here)
{parent_hint}

## Publish plan (follow this tree and naming; adjust only if the SRS contradicts)
{plan_text[:120_000]}

## SRS source file (read this file with your Read tool — do not guess content)
Absolute path: {srs_path}

## Rules
- Use Notion MCP only (no fake URLs). Create child pages under the parent above.
- **Structure:** (1) Create a **Dashboard** child under the root with project context and **links to every first-level SRS TOC section page**. (2) Create **one child page per first-level TOC section** (in TOC order). Page titles **must include SRS section numbers** when present (e.g. `4.1 Scope`). (3) If a section body is very long, split into additional child pages but **keep numbering visible** in titles or lead paragraphs. (4) Preserve requirement IDs (`RF-`, `RNF-`, `REQ-`) exactly. (5) Where the SRS contains URLs in citations, footnotes, or references, **add working hyperlinks** (markdown or Notion) — never invent URLs. (6) Do not invent content absent from the SRS file.
- **Lossless body (critical):** For each SRS section mapped to a Notion page, copy the **entire** section body: **every** paragraph, bullet/numbered list item, markdown **table** (all rows), **fenced code block**, and inline emphasis/code as faithfully as Notion blocks allow. **Do not summarize, shorten, or skip** subsubsections that belong to that section. If Notion size limits apply, continue on a linked child page titled with the same section number plus ` (continued)` and move overflow there without deleting meaning.
- A follow-up automated audit will re-open pages; omissions will be flagged and must be fixed—prefer getting it right in this pass.

## Output (plain text for the orchestrator)
Return a markdown execution log listing every page you created with **title** and **Notion URL** (or page id) on its own line. Start with PUBLISH_OK if everything succeeded, or PUBLISH_PARTIAL / PUBLISH_FAILED with reasons.
"""

        return run_claude_code_print(prompt, timeout_sec=timeout)
