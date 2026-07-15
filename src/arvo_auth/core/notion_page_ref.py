"""Resolve Notion page URLs and UUIDs for crews and tools."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from urllib.parse import unquote

from arvo_auth.core.tools.notion_claude_delegate import normalize_notion_page_id

_DASHED_UUID = re.compile(
    r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
    re.I,
)
_HEX32 = re.compile(r"([0-9a-f]{32})", re.I)


def _env_first(*names: str) -> str:
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""


def extract_page_id_from_notion_url(url: str) -> tuple[str | None, str | None]:
    """Extract a formatted Notion UUID from a notion.so / notion.site URL."""
    raw = unquote(url.strip())
    if not raw:
        return None, "Empty Notion URL."

    dashed = _DASHED_UUID.search(raw)
    if dashed:
        return normalize_notion_page_id(dashed.group(1))

    path = raw.split("?")[0].split("#")[0]
    tail = path.rstrip("/").split("/")[-1]
    for part in reversed(tail.split("-")):
        compact = part.replace("-", "")
        if len(compact) == 32 and all(c in "0123456789abcdef" for c in compact.lower()):
            return normalize_notion_page_id(compact)

    for match in reversed(_HEX32.findall(raw.replace("-", ""))):
        if len(match) == 32:
            return normalize_notion_page_id(match)

    return None, f"Could not extract Notion page id from URL: {url[:160]}"


def notion_page_url_from_id(page_id: str) -> tuple[str | None, str | None]:
    """Build a canonical notion.so URL from a page UUID."""
    fmt, err = normalize_notion_page_id(page_id)
    if err:
        return None, err
    assert fmt is not None
    return f"https://www.notion.so/{fmt.replace('-', '')}", None


@dataclass(frozen=True)
class NotionPageRef:
    """Notion page reference preferring URL for MCP prompts; UUID when extractable."""

    url: str
    page_id: str | None = None

    @classmethod
    def from_url_or_id(cls, raw: str) -> tuple[NotionPageRef | None, str | None]:
        value = raw.strip()
        if not value:
            return None, "Empty Notion page reference."

        if value.startswith("http://") or value.startswith("https://"):
            page_id, _ = extract_page_id_from_notion_url(value)
            return cls(url=value, page_id=page_id), None

        page_id, err = normalize_notion_page_id(value)
        if err:
            return None, err
        url, url_err = notion_page_url_from_id(value)
        if url_err or not url:
            return None, url_err or "Failed to build Notion URL from page id."
        return cls(url=url, page_id=page_id), None

    def prompt_hint(self) -> str:
        return f"Notion page URL: {self.url}"


def resolve_notion_page_ref(
    *,
    url_env_names: tuple[str, ...],
    id_env_names: tuple[str, ...] = (),
    label: str = "Notion page",
) -> tuple[NotionPageRef | None, str | None]:
    """Resolve a page ref from env vars, preferring URL variables over legacy UUID vars."""
    for name in url_env_names:
        val = _env_first(name)
        if val:
            return NotionPageRef.from_url_or_id(val)

    for name in id_env_names:
        val = _env_first(name)
        if val:
            return NotionPageRef.from_url_or_id(val)

    env_list = ", ".join(url_env_names + id_env_names)
    return None, f"Missing {label} URL. Set one of: {env_list}"
