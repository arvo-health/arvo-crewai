"""Create Notion child pages under a parent page (Notion REST API)."""

from __future__ import annotations

import os
import re
from typing import Any, Type

import httpx
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from arvo_auth_orchestrator.tools.notion_api_common import (
    NOTION_BASE,
    format_notion_uuid,
    notion_headers,
)

_MAX_RICH = 1900
_CHUNK_BLOCKS = 90


def _rich_paragraph(text: str) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": text[:_MAX_RICH]},
                }
            ]
        },
    }


def _heading(level: int, text: str) -> dict[str, Any]:
    key = {1: "heading_1", 2: "heading_2", 3: "heading_3"}[level]
    return {
        "object": "block",
        "type": key,
        key: {
            "rich_text": [
                {"type": "text", "text": {"content": text[:_MAX_RICH]}}
            ]
        },
    }


def _divider() -> dict[str, Any]:
    return {"object": "block", "type": "divider", "divider": {}}


def _bulleted(text: str) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [
                {"type": "text", "text": {"content": text[:_MAX_RICH]}}
            ]
        },
    }


def _callout(text: str, color: str = "red_background") -> dict[str, Any]:
    return {
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": [
                {"type": "text", "text": {"content": text[:_MAX_RICH]}}
            ],
            "icon": {"type": "emoji", "emoji": "⚠️"},
            "color": color,
        },
    }


def markdown_to_notion_blocks(markdown: str) -> list[dict[str, Any]]:
    """Lightweight line-based markdown to Notion blocks (no full MD spec)."""
    blocks: list[dict[str, Any]] = []
    in_code = False
    code_buf: list[str] = []

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        if line.strip().startswith("```"):
            if in_code:
                body = "\n".join(code_buf)[:_MAX_RICH]
                blocks.append(
                    {
                        "object": "block",
                        "type": "code",
                        "code": {
                            "rich_text": [
                                {"type": "text", "text": {"content": body}}
                            ],
                            "language": "markdown",
                        },
                    }
                )
                code_buf = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_buf.append(line)
            continue

        if line.strip() == "---":
            blocks.append(_divider())
            continue
        if re.match(r"^#\s+", line):
            blocks.append(_heading(1, re.sub(r"^#\s+", "", line).strip()))
            continue
        if re.match(r"^##\s+", line):
            blocks.append(_heading(2, re.sub(r"^##\s+", "", line).strip()))
            continue
        if re.match(r"^###\s+", line):
            blocks.append(_heading(3, re.sub(r"^###\s+", "", line).strip()))
            continue
        if re.match(r"^[-*]\s+", line):
            blocks.append(_bulleted(re.sub(r"^[-*]\s+", "", line).strip()))
            continue
        if re.match(r"^(RF-|RNF-|REQ-)", line.strip(), re.I):
            blocks.append(_callout(line.strip(), "yellow_background"))
            continue
        if line.strip():
            blocks.append(_rich_paragraph(line.strip()))
    return blocks


class NotionPublishChildPageInput(BaseModel):
    parent_page_id: str = Field(
        default="",
        description="Parent Notion page UUID. If empty, uses NOTION_SRS_PARENT_PAGE_ID from the environment.",
    )
    title: str = Field(..., description="Title of the new child page.")
    body_markdown: str = Field(
        ...,
        description="Markdown body; converted to Notion blocks (headings, lists, callouts for RF/RNF lines).",
    )


class NotionPublishChildPageTool(BaseTool):
    name: str = "notion_create_child_page"
    description: str = (
        "Create ONE child page under a parent Notion page using the API. Returns the "
        "new page id and URL for chaining further sub-pages. Requires NOTION_API_KEY and "
        "a parent page shared with the integration. Chunks content if it exceeds API limits."
    )
    args_schema: Type[BaseModel] = NotionPublishChildPageInput

    def _run(self, parent_page_id: str, title: str, body_markdown: str) -> str:
        if not os.getenv("NOTION_API_KEY", "").strip():
            return "NOTION_API_KEY is not set."

        headers = notion_headers()
        parent_raw = (parent_page_id or "").strip() or os.getenv(
            "NOTION_SRS_PARENT_PAGE_ID", ""
        ).strip()
        if not parent_raw:
            return (
                "Missing parent: pass parent_page_id or set NOTION_SRS_PARENT_PAGE_ID "
                "to the Notion root page UUID (shared with the integration)."
            )

        parent_fmt, err = format_notion_uuid(parent_raw)
        if err:
            return err
        assert parent_fmt is not None

        blocks = markdown_to_notion_blocks(body_markdown or "(empty)")
        if not blocks:
            blocks = [_rich_paragraph("(no body)")]

        first_batch = blocks[:_CHUNK_BLOCKS]
        rest = blocks[_CHUNK_BLOCKS:]

        payload: dict[str, Any] = {
            "parent": {"type": "page_id", "page_id": parent_fmt},
            "properties": {
                "title": {
                    "title": [
                        {"type": "text", "text": {"content": title[:2000]}}
                    ]
                }
            },
            "children": first_batch,
        }

        try:
            with httpx.Client(timeout=120.0) as client:
                r = client.post(f"{NOTION_BASE}/pages", headers=headers, json=payload)
                if r.status_code != 200:
                    return f"Notion create page error {r.status_code}: {r.text[:1200]}"

                data = r.json()
                new_id = data.get("id", "")
                url = data.get("url", "")

                while rest:
                    batch = rest[:_CHUNK_BLOCKS]
                    rest = rest[_CHUNK_BLOCKS:]
                    ar = client.patch(
                        f"{NOTION_BASE}/blocks/{new_id}/children",
                        headers=headers,
                        json={"children": batch},
                    )
                    if ar.status_code != 200:
                        return (
                            f"Page created {new_id} but append failed {ar.status_code}: "
                            f"{ar.text[:800]}"
                        )

                return (
                    f"Created Notion child page.\npage_id: {new_id}\nurl: {url}\n"
                    f"Use this page_id as parent_page_id for nested sub-pages."
                )
        except httpx.HTTPError as exc:
            return f"HTTP error: {exc}"
