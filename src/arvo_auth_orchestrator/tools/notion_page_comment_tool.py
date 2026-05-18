"""Post a top-level comment on a Notion page via REST API."""

from __future__ import annotations

import os
from typing import Type

import httpx
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from arvo_auth_orchestrator.tools.notion_api_common import (
    NOTION_BASE,
    format_notion_uuid,
    notion_headers,
)

_MAX_MARKDOWN = 1900


class NotionPageCommentInput(BaseModel):
    page_id: str = Field(
        ...,
        description="Notion page UUID (with or without dashes) to attach the comment to.",
    )
    markdown_comment: str = Field(
        ...,
        description=(
            "Comment body in **inline** markdown only (bold, italic, links, inline code). "
            "Avoid headings, lists, and code fences — Notion comment markdown is inline-only."
        ),
    )


class NotionPostPageCommentTool(BaseTool):
    name: str = "notion_post_page_comment"
    description: str = (
        "Create a single comment on a Notion page (parent.page_id). Requires NOTION_API_KEY "
        "and the integration must have **insert comment** capability enabled in the Notion "
        "developer portal. Respects ARVO_GAP_COMMENT_DRY_RUN=1 to log without posting."
    )
    args_schema: Type[BaseModel] = NotionPageCommentInput

    def _run(self, page_id: str, markdown_comment: str) -> str:
        token = os.getenv("NOTION_API_KEY", "").strip()
        if not token:
            return "ERROR: NOTION_API_KEY is not set."

        fmt, err = format_notion_uuid(page_id.strip())
        if err:
            return f"ERROR: {err}"

        body_md = markdown_comment.strip()
        if not body_md:
            return "ERROR: empty markdown_comment."

        if len(body_md) > _MAX_MARKDOWN:
            body_md = body_md[: _MAX_MARKDOWN - 3] + "..."

        dry = os.getenv("ARVO_GAP_COMMENT_DRY_RUN", "").strip().lower() in (
            "1",
            "true",
            "yes",
        )
        if dry:
            return (
                "DRY_RUN: would post comment on page "
                f"{fmt} ({len(body_md)} chars). NOT sent to Notion."
            )

        payload = {
            "parent": {"page_id": fmt},
            "markdown": body_md,
        }

        try:
            with httpx.Client(timeout=45.0) as client:
                r = client.post(
                    f"{NOTION_BASE}/comments",
                    headers=notion_headers(),
                    json=payload,
                )
        except OSError as exc:
            return f"ERROR: Notion comment request failed: {exc}"

        if r.status_code != 200:
            return (
                f"ERROR: Notion comment HTTP {r.status_code}: {r.text[:1500]}. "
                "If 403, enable insert-comment capability for the integration."
            )

        data = r.json()
        cid = data.get("id", "")
        return f"OK: comment created. comment_id={cid} page_id={fmt}"
