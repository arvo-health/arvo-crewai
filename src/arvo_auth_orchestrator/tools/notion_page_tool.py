"""Fetch Notion page content via the official API or via Claude Code CLI (MCP)."""

from __future__ import annotations

import os
from typing import Any, Type

import httpx
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from arvo_auth_orchestrator.tools.notion_claude_delegate import (
    fetch_notion_page_via_claude_code,
    normalize_notion_page_id,
)

NOTION_VERSION = "2022-06-28"
_MAX_BLOCKS = 400


def _rich_text_to_plain(rich: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for span in rich or []:
        if isinstance(span, dict) and "plain_text" in span:
            parts.append(span.get("plain_text", ""))
    return "".join(parts).strip()


def _block_to_line(block: dict[str, Any]) -> str | None:
    btype = block.get("type")
    if not btype or btype not in block:
        return None
    payload = block[btype]
    rich = payload.get("rich_text", [])
    text = _rich_text_to_plain(rich)
    if btype == "paragraph":
        return text if text else ""
    if btype in ("heading_1", "heading_2", "heading_3"):
        level = {"heading_1": "#", "heading_2": "##", "heading_3": "###"}[btype]
        return f"{level} {text}".strip()
    if btype == "bulleted_list_item":
        return f"- {text}" if text else "-"
    if btype == "numbered_list_item":
        return f"1. {text}" if text else "1."
    if btype == "to_do":
        box = "[x]" if payload.get("checked") else "[ ]"
        return f"{box} {text}".strip()
    if btype == "quote":
        return f"> {text}" if text else ">"
    if btype in ("code", "equation"):
        return text
    if btype == "divider":
        return "---"
    return f"[{btype}] {text}".strip() if text else f"[{btype}]"


class NotionPageReadInput(BaseModel):
    page_id: str = Field(
        ...,
        description="Notion page UUID (with or without dashes) from the docs database.",
    )


class NotionPageReadTool(BaseTool):
    name: str = "fetch_notion_page_text"
    description: str = (
        "Retrieve readable text from a Notion page. Uses the Notion REST API when "
        "NOTION_API_KEY is set (unless NOTION_VIA_CLAUDE_CODE=1 forces delegation). "
        "If NOTION_API_KEY is unset, automatically delegates to the local Claude Code CLI "
        "(`claude -p`, Notion MCP) — set NOTION_VIA_CLAUDE_CODE=0 to refuse that path."
    )
    args_schema: Type[BaseModel] = NotionPageReadInput

    def _run(self, page_id: str) -> str:
        fmt_id, err = normalize_notion_page_id(page_id)
        if err:
            return err
        assert fmt_id is not None

        token = os.getenv("NOTION_API_KEY", "").strip()
        via = os.getenv("NOTION_VIA_CLAUDE_CODE", "").strip().lower()
        force_claude = via in ("1", "true", "yes")
        disable_claude = via in ("0", "false", "no")

        if not token and disable_claude:
            return (
                "NOTION_API_KEY is not set and NOTION_VIA_CLAUDE_CODE disables delegation. "
                "Set NOTION_API_KEY for API access, or unset NOTION_VIA_CLAUDE_CODE (or set to 1) "
                "to use the Claude Code CLI with your Notion MCP. Install the `claude` CLI."
            )

        if not token or force_claude:
            return fetch_notion_page_via_claude_code(fmt_id)

        headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        }

        lines: list[str] = []
        try:
            with httpx.Client(timeout=60.0) as client:
                page = client.get(
                    f"https://api.notion.com/v1/pages/{fmt_id}", headers=headers
                )
                if page.status_code != 200:
                    return f"Notion pages error {page.status_code}: {page.text[:500]}"

                title = "Notion page"
                props = page.json().get("properties", {})
                for _k, pv in props.items():
                    if isinstance(pv, dict) and pv.get("type") == "title":
                        chunks = pv.get("title", [])
                        title = _rich_text_to_plain(chunks) or title
                        break
                lines.append(f"# {title}")
                lines.append("")

                cursor: str | None = None
                count = 0
                block_id = fmt_id
                while count < _MAX_BLOCKS:
                    params: dict[str, str] = {}
                    if cursor:
                        params["start_cursor"] = cursor
                    r = client.get(
                        f"https://api.notion.com/v1/blocks/{block_id}/children",
                        headers=headers,
                        params=params,
                    )
                    if r.status_code != 200:
                        lines.append(f"(blocks error {r.status_code})")
                        break
                    data = r.json()
                    stop_outer = False
                    for block in data.get("results", []):
                        count += 1
                        if count > _MAX_BLOCKS:
                            stop_outer = True
                            break
                        btype = block.get("type")
                        if btype in ("child_page", "child_database"):
                            continue
                        line = _block_to_line(block)
                        if line is not None:
                            lines.append(line)
                        if block.get("has_children") and block.get("type") not in (
                            "table",
                            "column_list",
                        ):
                            nested = self._fetch_nested(
                                client, headers, block["id"], depth=1, max_depth=2
                            )
                            lines.extend(nested)
                    if stop_outer:
                        break
                    if not data.get("has_more"):
                        break
                    cursor = data.get("next_cursor")
                    if not cursor:
                        break

        except httpx.HTTPError as exc:
            return f"HTTP error talking to Notion: {exc}"

        return "\n".join(lines) if lines else "(empty page)"

    def _fetch_nested(
        self,
        client: httpx.Client,
        headers: dict[str, str],
        block_id: str,
        depth: int,
        max_depth: int,
    ) -> list[str]:
        if depth > max_depth:
            return ["  " * depth + "(nested content omitted)"]
        out: list[str] = []
        cursor: str | None = None
        while True:
            params: dict[str, str] = {}
            if cursor:
                params["start_cursor"] = cursor
            r = client.get(
                f"https://api.notion.com/v1/blocks/{block_id}/children",
                headers=headers,
                params=params,
            )
            if r.status_code != 200:
                break
            data = r.json()
            for block in data.get("results", []):
                line = _block_to_line(block)
                if line:
                    out.append("  " * depth + line)
                if block.get("has_children") and depth < max_depth:
                    out.extend(
                        self._fetch_nested(
                            client, headers, block["id"], depth + 1, max_depth
                        )
                    )
            if not data.get("has_more"):
                break
            cursor = data.get("next_cursor")
            if not cursor:
                break
        return out
