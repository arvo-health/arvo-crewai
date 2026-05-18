"""Shared Notion REST constants."""

NOTION_VERSION = "2022-06-28"
NOTION_BASE = "https://api.notion.com/v1"


def format_notion_uuid(raw: str) -> tuple[str | None, str | None]:
    """Return (formatted_uuid, error_message)."""
    normalized = raw.replace("-", "").strip().lower()
    if len(normalized) != 32 or not all(c in "0123456789abcdef" for c in normalized):
        return None, "Invalid UUID: expected 32 hex characters."
    fmt = (
        f"{normalized[:8]}-{normalized[8:12]}-{normalized[12:16]}-"
        f"{normalized[16:20]}-{normalized[20:]}"
    )
    return fmt, None


def notion_headers() -> dict[str, str]:
    import os

    token = os.getenv("NOTION_API_KEY", "").strip()
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }
