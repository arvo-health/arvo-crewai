"""Scan Notion pages under the SRS workspace root for comments via Claude Code CLI (MCP).

Does **not** read any on-disk outputs from other crews (no publish_plan, execution_log, SRS,
or gaps files). Discovery is entirely from Notion MCP starting at NOTION_SRS_PARENT_PAGE_ID /
NOTION_SRS_PARENT_URL.
"""

from __future__ import annotations

import os
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from arvo_auth.core.tools.notion_claude_delegate import run_claude_code_print


class NotionCollectPageCommentsInput(BaseModel):
    """Unused; the tool delegates to Claude + Notion MCP only."""

    unused: str = Field(default="", description="Leave empty.")


class NotionCollectSrsPageCommentsViaClaudeTool(BaseTool):
    name: str = "notion_collect_srs_page_comments_via_claude"
    description: str = (
        "Starting at NOTION_SRS_PARENT_PAGE_ID or NOTION_SRS_PARENT_URL, use Notion MCP to "
        "recursively list **all** child pages under the workspace root, read each page's body "
        "and **all** page-level discussion threads / comments, and return a structured markdown "
        "report. Does not read local markdown outputs from other crews. Timeout: "
        "NOTION_COMMENT_SCAN_CLAUDE_TIMEOUT_SEC (default 3600)."
    )
    args_schema: Type[BaseModel] = NotionCollectPageCommentsInput

    def _run(self, unused: str = "") -> str:
        parent_id = os.getenv("NOTION_SRS_PARENT_PAGE_ID", "").strip()
        parent_url = os.getenv("NOTION_SRS_PARENT_URL", "").strip()
        if not parent_id and not parent_url:
            return (
                "Set NOTION_SRS_PARENT_PAGE_ID (Notion page UUID) or NOTION_SRS_PARENT_URL "
                "for the Notion comment scan."
            )

        parent_hint = (
            f"Workspace root parent UUID: {parent_id}"
            if parent_id
            else f"Workspace root parent URL: {parent_url}"
        )

        timeout = int(os.getenv("NOTION_COMMENT_SCAN_CLAUDE_TIMEOUT_SEC", "3600"))

        prompt = f"""You are the SRS Change Steward performing a **Notion-only page and comment audit**.
You have Notion MCP (same as interactive Claude Code).

**Hard rule:** Do **not** read any local project files (no `outputs/`, no `SRS.md`, no publish
logs, no gaps manifests). All facts come from Notion MCP and the workspace root below.

## Workspace root (attach traversal here)
{parent_hint}

## Mandatory procedure
1. Using Notion MCP only, start at the workspace root page above. Perform a **depth-first**
   traversal of the **entire page tree**: every direct child, every nested sub-page, and any
   pages discovered only through navigation (continuations, linked sub-pages under this root).
   Build the **complete ordered list** of visited pages (title + canonical Notion URL or page id
   for each). Do not skip pages without comments in the tree walk — they still belong in the
   inventory.
2. For **each** visited page, retrieve **all** discussion threads / page comments / inline
   comment threads available through MCP. If a page has zero comments, record `_(sem comentários)_`
   under that page's heading in your notes.
3. For each non-empty comment, capture: author label (if visible), timestamp (if visible),
   raw comment text, and the nearest on-page anchor when MCP exposes it (heading, block, or
   first line of the commented region).
4. When a comment clearly implies a change to requirements or documentation, assign a stable
   id `C-001`, `C-002`, … in **depth-first page order**, then top-to-bottom comment order as MCP
   returns. Each `C-*` row must include:
   - `C-id`
   - `suggested_change_type` ∈ {{`add`, `modify`, `remove`, `rename`, `clarify`}}
   - `page_title` + **Notion URL or page id** (from MCP only — never guessed)
   - `target_hint` (section numbers, RF-/RNF-/REQ- **only if they appear verbatim** in the
     comment text or in the **Notion page body** you read via MCP — do not import identifiers
     from any external file)
   - `comment_excerpt` (≤ 3 sentences, verbatim when possible)
   - `steward_interpretation` (one sentence in pt-BR)

5. If a comment is purely social (`LGTM`, thanks) with no actionable content, list it under
   `## Comentários sem impacto` instead of assigning a `C-id`.

6. Do **not** invent pages, URLs, or comment text. If MCP cannot list children or comments for a
   page, document under `## Erros de leitura` with the page URL/id and the error.

## Output (plain text / markdown for the orchestrator)
First line exactly one of: `COMMENT_SCAN_OK`, `COMMENT_SCAN_PARTIAL`, or `COMMENT_SCAN_FAILED`.

Then markdown sections in **pt-BR**:
- `## Resumo` — total pages visited, pages with ≥1 comment, total `C-*` rows.
- `## Inventário de páginas (Notion)` — markdown table **required**:
  `ordem | depth | page_title | page_url_or_id | teve_comentários (sim/não)` for **every**
  visited page. This inventory is the only allowed source of Notion URLs for downstream diff
  planning in this workflow.
- `## Sugestões a partir de comentários (C-*)` — table:
  `C-id | suggested_change_type | page_title | page_url_or_id | target_hint | comment_excerpt |
   steward_interpretation`.
- `## Comentários sem impacto` (optional).
- `## Erros de leitura` (optional).

Do not edit Notion in this pass — reporting only. Do not read local disk beyond what your MCP
tools implicitly require.
"""

        return run_claude_code_print(prompt, timeout_sec=timeout)
