"""Append a new entry to the SRS Versions/Updates page on Notion via Claude Code CLI (MCP)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from arvo_auth.core.tools.notion_claude_delegate import run_claude_code_print


def _project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _publish_execution_log_path() -> Path:
    return _project_root() / "outputs" / "engineering" / "notion_export" / "publish_execution_log.md"


class NotionUpdateVersionsInput(BaseModel):
    version_number: str = Field(
        ...,
        description="New semantic version string to record on the Notion Versions page (e.g. 1.4.0).",
    )
    iso_date: str = Field(
        ...,
        description="ISO-8601 date (YYYY-MM-DD) when the change set was applied.",
    )
    summary_markdown: str = Field(
        ...,
        description=(
            "Short markdown summary of the applied changes. Bullet list per decision id is "
            "preferred. This text is appended to the Notion Versions/Updates page as a new entry."
        ),
    )


class NotionUpdateVersionsViaClaudeTool(BaseTool):
    name: str = "notion_update_versions_section_via_claude"
    description: str = (
        "Append a new version entry to the SRS Versions/Updates page on Notion (or create the "
        "page under the workspace root if it does not exist yet). Uses Claude Code CLI + MCP; "
        "requires NOTION_SRS_PARENT_PAGE_ID or NOTION_SRS_PARENT_URL. Timeout: "
        "NOTION_VERSIONS_UPDATE_CLAUDE_TIMEOUT_SEC (default 600)."
    )
    args_schema: Type[BaseModel] = NotionUpdateVersionsInput

    def _run(self, version_number: str, iso_date: str, summary_markdown: str) -> str:
        version = (version_number or "").strip()
        date_str = (iso_date or "").strip()
        summary = (summary_markdown or "").strip()
        if not version or not date_str or not summary:
            return (
                "Missing one of version_number / iso_date / summary_markdown. All three are "
                "required to record a new SRS version entry."
            )

        parent_id = os.getenv("NOTION_SRS_PARENT_PAGE_ID", "").strip()
        parent_url = os.getenv("NOTION_SRS_PARENT_URL", "").strip()
        if not parent_id and not parent_url:
            return (
                "Set NOTION_SRS_PARENT_PAGE_ID (Notion page UUID) or NOTION_SRS_PARENT_URL "
                "so the MCP run knows where to find or create the Versions page."
            )

        parent_hint = (
            f"Workspace root parent UUID: {parent_id}"
            if parent_id
            else f"Workspace root parent URL: {parent_url}"
        )

        timeout = int(os.getenv("NOTION_VERSIONS_UPDATE_CLAUDE_TIMEOUT_SEC", "600"))

        prompt = f"""You are the SRS Change Steward updating the SRS Versions/Updates page on Notion via MCP.
Do not use REST APIs or invent URLs.

## Workspace root
{parent_hint}

## Execution log of the SRS publish (for locating the Versions/Updates page among existing children)
{_publish_execution_log_path()}

## New version entry to record
- Version: {version}
- Date (ISO): {date_str}

## Summary markdown to append (faithful copy)
{summary}

## Procedure
1. Locate the Versions/Updates page among the children of the workspace root. Match by case-insensitive title containing one of: "Atualizações", "Updates", "Histórico de versões", "Versões", "Version history".
2. If no such page exists, create it as a direct child of the workspace root with title "Atualizações / Updates".
3. **Prepend** a new section block titled `## v{version} — {date_str}` (or update the page's heading style equivalently), followed by the summary markdown.
4. Preserve previous version entries — never delete or rewrite older ones.
5. Use Notion MCP only. Return the final page URL.

## Output (plain text for the orchestrator)
First line exactly one of: `VERSIONS_OK`, `VERSIONS_CREATED`, or `VERSIONS_FAILED`.
Then a markdown bullet with the page URL (or page id) and the version recorded. If failed, explain why on the next line.
"""

        return run_claude_code_print(prompt, timeout_sec=timeout)
