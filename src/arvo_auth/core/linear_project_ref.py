"""Resolve Linear project URLs and legacy name/id references."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from urllib.parse import unquote

_LINEAR_PROJECT_URL = re.compile(
    r"https?://linear\.app/(?:[^/]+/)?project/([^/?#]+)",
    re.I,
)
_DASHED_UUID = re.compile(
    r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
    re.I,
)
_HEX12 = re.compile(r"^[0-9a-f]{12}$", re.I)


def _env_first(*names: str) -> str:
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""


def _normalize_linear_project_url(url: str) -> str:
    raw = unquote(url.strip())
    if not raw:
        return ""
    base = raw.split("?")[0].split("#")[0].rstrip("/")
    return base


def extract_slug_from_linear_project_url(url: str) -> tuple[str | None, str | None]:
    """Extract project slug from a linear.app project URL."""
    normalized = _normalize_linear_project_url(url)
    if not normalized:
        return None, "Empty Linear project URL."

    match = _LINEAR_PROJECT_URL.search(normalized)
    if not match:
        return None, f"Not a Linear project URL: {url[:160]}"

    slug = match.group(1).strip()
    if not slug:
        return None, f"Missing project slug in URL: {url[:160]}"
    return slug, None


def extract_short_id_from_project_slug(slug: str) -> str | None:
    """Linear project URLs often end with a 12-character hex id after the slug."""
    tail = slug.rsplit("-", 1)
    if len(tail) == 2 and _HEX12.match(tail[1]):
        return tail[1].lower()
    return None


@dataclass(frozen=True)
class LinearProjectRef:
    """Linear project reference preferring full URL for MCP prompts."""

    url: str
    slug: str | None = None
    short_id: str | None = None
    legacy_name: str = ""
    legacy_id: str = ""

    @classmethod
    def from_url_or_legacy(cls, raw: str) -> tuple[LinearProjectRef | None, str | None]:
        value = raw.strip()
        if not value:
            return None, "Empty Linear project reference."

        if value.startswith("http://") or value.startswith("https://"):
            normalized = _normalize_linear_project_url(value)
            slug, err = extract_slug_from_linear_project_url(normalized)
            if err or not slug:
                return None, err
            return (
                cls(
                    url=normalized,
                    slug=slug,
                    short_id=extract_short_id_from_project_slug(slug),
                ),
                None,
            )

        dashed = _DASHED_UUID.fullmatch(value)
        if dashed:
            return cls(url="", legacy_id=dashed.group(1)), None

        if _HEX12.match(value):
            return cls(url="", short_id=value.lower(), legacy_id=value.lower()), None

        return cls(url="", legacy_name=value), None

    def is_configured(self) -> bool:
        return bool(self.url or self.legacy_name or self.legacy_id or self.short_id)

    def prompt_hint(self) -> str:
        if self.url:
            return f"Linear project URL: {self.url}"
        if self.legacy_id:
            return f"Linear project ID: {self.legacy_id}"
        if self.short_id:
            return f"Linear project short ID: {self.short_id}"
        if self.legacy_name:
            return f"Linear project name: {self.legacy_name}"
        return "Linear project: (unset)"


def resolve_linear_project_ref(
    *,
    url_env_names: tuple[str, ...],
    legacy_env_names: tuple[str, ...] = (),
) -> tuple[LinearProjectRef | None, str | None]:
    """Resolve a project ref from env vars, preferring URL variables."""
    for name in url_env_names:
        val = _env_first(name)
        if val:
            return LinearProjectRef.from_url_or_legacy(val)

    for name in legacy_env_names:
        val = _env_first(name)
        if val:
            return LinearProjectRef.from_url_or_legacy(val)

    return None, None
