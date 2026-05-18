"""Apply an approved SRS-change diff to Notion pages via Claude Code CLI (MCP)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from arvo_auth_orchestrator.tools.notion_claude_delegate import run_claude_code_print
from arvo_auth_orchestrator.tools.srs_publish_read_tool import _resolve_srs_path


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _diff_path() -> Path:
    return _project_root() / "outputs" / "srs_meeting_update" / "notion_changes_diff.md"


def _manifest_path() -> Path:
    return _project_root() / "outputs" / "srs_meeting_update" / "srs_changes_manifest.md"


def _publish_plan_path() -> Path:
    return _project_root() / "outputs" / "notion_export" / "publish_plan.md"


def _publish_execution_log_path() -> Path:
    return _project_root() / "outputs" / "notion_export" / "publish_execution_log.md"


class NotionApplySrsChangesInput(BaseModel):
    """Tool reads the approved diff from disk; arguments are unused."""

    unused: str = Field(default="", description="Leave empty.")


class NotionApplySrsChangesViaClaudeTool(BaseTool):
    name: str = "notion_apply_srs_changes_via_claude"
    description: str = (
        "Apply the approved SRS-change diff (outputs/srs_meeting_update/notion_changes_diff.md) "
        "to the live Notion pages via a single Claude Code subprocess with Notion MCP. Supports "
        "insert_block, update_block, remove_block, rename_page, add_page, and remove_page "
        "operations as encoded in the diff. Requires NOTION_SRS_PARENT_PAGE_ID or "
        "NOTION_SRS_PARENT_URL. Timeout: NOTION_APPLY_CHANGES_CLAUDE_TIMEOUT_SEC (default 1800)."
    )
    args_schema: Type[BaseModel] = NotionApplySrsChangesInput

    def _run(self, unused: str = "") -> str:
        diff_file = _diff_path()
        if not diff_file.is_file():
            return (
                f"Approved diff not found at {diff_file}. Run the planning crew first and "
                "re-run only after explicit human approval."
            )

        diff_text = diff_file.read_text(encoding="utf-8", errors="replace")
        if not diff_text.strip():
            return f"Diff file is empty: {diff_file}. Nothing to apply."

        manifest_file = _manifest_path()
        manifest_text = (
            manifest_file.read_text(encoding="utf-8", errors="replace")
            if manifest_file.is_file()
            else "(srs_changes_manifest.md not found — proceed using the diff alone.)"
        )

        parent_id = os.getenv("NOTION_SRS_PARENT_PAGE_ID", "").strip()
        parent_url = os.getenv("NOTION_SRS_PARENT_URL", "").strip()
        if not parent_id and not parent_url:
            return (
                "Set NOTION_SRS_PARENT_PAGE_ID (Notion page UUID) or NOTION_SRS_PARENT_URL "
                "so the MCP run knows the workspace root."
            )

        srs_path, srs_err = _resolve_srs_path()
        srs_hint = str(srs_path) if srs_path is not None else f"(SRS path unresolved: {srs_err})"

        parent_hint = (
            f"Workspace root parent UUID: {parent_id}"
            if parent_id
            else f"Workspace root parent URL: {parent_url}"
        )

        timeout = int(os.getenv("NOTION_APPLY_CHANGES_CLAUDE_TIMEOUT_SEC", "1800"))

        prompt = f"""You are the SRS Change Steward applying an approved diff to Notion via MCP.
You have Notion MCP (same setup as interactive Claude Code). Do not use REST APIs or invent URLs.

## Workspace root
{parent_hint}

## SRS source file (local reference; do not overwrite from here — only read for cross-checks)
{srs_hint}

## Source-of-truth on-disk artefacts (read in full if any excerpt below is truncated)
- Approved diff: {_diff_path()}
- Change manifest: {_manifest_path()}
- Publish plan: {_publish_plan_path()}
- Publish execution log (page titles / URLs): {_publish_execution_log_path()}

## Approved diff (excerpt — first ~80k chars)
{diff_text[:80_000]}

## Change manifest (excerpt — first ~30k chars)
{manifest_text[:30_000]}

## Mandatory execution procedure
1. Re-read the **complete** diff and execution log from disk for the exact page URLs / page IDs you must touch.
2. For each operation in the diff, in order:
   - `add_page`: create the child page under the parent indicated by the diff (page title MUST include the SRS section number when present).
   - `remove_page`: archive/delete the target page in Notion (prefer archive if your MCP supports it).
   - `rename_page`: rename the existing Notion page; if requirement IDs (RF-/RNF-/REQ-) appear in titles, update them consistently.
   - `insert_block` / `update_block` / `remove_block`: edit the target page's blocks at the anchor indicated (heading, paragraph after a known phrase, or table row). Insert markdown faithfully (no summaries); preserve numbering and IDs.
3. Use Notion MCP only. Do not invent page URLs or IDs not present in the diff/log. If the diff references an anchor that no longer exists, log it as `MISSING_ANCHOR` and continue with the remaining operations.
4. Do **not** edit the Versions/Updates section of the SRS here — that is handled by a separate step.
5. After all operations: verify each modified page by re-reading it once and confirming the requested change is visible.

## Output (plain text for the orchestrator)
First line exactly one of: `APPLY_OK`, `APPLY_PARTIAL`, or `APPLY_FAILED`.
Then markdown bullets — one per diff operation — with: decision id (e.g. D-001), operation type, target page URL or page id, status (OK / SKIPPED / ERROR), short detail or error reason.
End with a one-line summary: total ops, ok, skipped, error.
"""

        return run_claude_code_print(prompt, timeout_sec=timeout)
