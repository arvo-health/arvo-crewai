"""Search Notion workspace pages via REST API (for gap/comment workflows)."""

from __future__ import annotations

import os
from typing import Any, Type

import httpx
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from arvo_auth_orchestrator.tools.notion_api_common import NOTION_BASE, notion_headers


class NotionSearchInput(BaseModel):
    query: str = Field(
        ...,
        description="Plain-text search query (e.g. section title or requirement theme).",
    )
    page_size: int = Field(
        default=8,
        ge=1,
        le=25,
        description="Max number of page results to return (1–25).",
    )


class NotionSearchPagesTool(BaseTool):
    name: str = "notion_search_pages"
    description: str = (
        "Search the Notion workspace for pages matching a query. Requires NOTION_API_KEY. "
        "Returns page id, title, and URL for each hit so you can pick the best page before "
        "posting a comment."
    )
    args_schema: Type[BaseModel] = NotionSearchInput

    def _run(self, query: str, page_size: int = 8) -> str:
        token = os.getenv("NOTION_API_KEY", "").strip()
        if not token:
            return "ERROR: NOTION_API_KEY is not set; Notion search is unavailable."

        q = query.strip()
        if not q:
            return "ERROR: empty search query."

        body: dict[str, Any] = {
            "query": q,
            "filter": {"value": "page", "property": "object"},
            "page_size": min(max(page_size, 1), 25),
        }

        try:
            with httpx.Client(timeout=45.0) as client:
                r = client.post(
                    f"{NOTION_BASE}/search",
                    headers=notion_headers(),
                    json=body,
                )
        except OSError as exc:
            return f"ERROR: Notion search request failed: {exc}"

        if r.status_code != 200:
            return f"ERROR: Notion search HTTP {r.status_code}: {r.text[:1200]}"

        data = r.json()
        results = data.get("results") or []
        if not results:
            return f"(no pages found for query: {q!r})"

        lines: list[str] = [f"Search results for {q!r} ({len(results)} page(s)):", ""]
        for item in results:
            pid = item.get("id", "")
            url = item.get("url", "") or item.get("public_url", "")
            title = "Untitled"
            props = item.get("properties") or {}
            for prop in props.values():
                if isinstance(prop, dict) and prop.get("type") == "title":
                    parts = prop.get("title") or []
                    chunks: list[str] = []
                    for p in parts:
                        if isinstance(p, dict) and p.get("type") == "text":
                            chunks.append(str(p.get("plain_text", "")))
                    merged = "".join(chunks).strip()
                    if merged:
                        title = merged
                    break
            lines.append(f"- page_id: {pid}")
            lines.append(f"  title: {title}")
            if url:
                lines.append(f"  url: {url}")
            lines.append("")

        return "\n".join(lines).strip()
