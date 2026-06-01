"""Delegate Notion page reads and full publish flows to Claude Code CLI (MCP)."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


def normalize_notion_page_id(page_id: str) -> tuple[str | None, str | None]:
    """Return (formatted_uuid, error_message)."""
    normalized = page_id.replace("-", "").strip().lower()
    if len(normalized) != 32 or not all(c in "0123456789abcdef" for c in normalized):
        return None, "Invalid page_id: expected a 32-character Notion UUID."
    fmt = (
        f"{normalized[:8]}-{normalized[8:12]}-{normalized[12:16]}-"
        f"{normalized[16:20]}-{normalized[20:]}"
    )
    return fmt, None


def default_claude_cwd() -> str:
    """Prefer Arvo workspace root (parent of orchestrator) for MCP / project files."""
    orch = Path(__file__).resolve().parents[4]
    parent = orch.parent
    if (parent / "second-brain").is_dir() or (parent / "arvo-auth").is_dir():
        return str(parent)
    return str(orch)


def run_claude_code_print(prompt: str, timeout_sec: int | None = None) -> str:
    """
    Run `claude -p` once. When timeout_sec is None, uses NOTION_CLAUDE_DELEGATE_TIMEOUT_SEC
    (default 600). Pass an explicit timeout for long publish runs.
    """
    claude = (os.getenv("CLAUDE_CODE_BIN") or "").strip() or shutil.which("claude")
    if not claude:
        return (
            "ERROR: Claude Code CLI not found. Install it or set CLAUDE_CODE_BIN to the full "
            "path of the `claude` executable."
        )

    cwd = (os.getenv("ARVO_CLAUDE_CODE_CWD") or "").strip() or default_claude_cwd()
    if timeout_sec is None:
        timeout_sec = int(os.getenv("NOTION_CLAUDE_DELEGATE_TIMEOUT_SEC", "600"))
    perm = (os.getenv("CLAUDE_CODE_PERMISSION_MODE") or "acceptEdits").strip()

    cmd = [
        claude,
        "-p",
        prompt,
        "--output-format",
        "text",
        "--permission-mode",
        perm,
    ]

    extra_args = os.getenv("CLAUDE_CODE_EXTRA_ARGS", "").strip()
    if extra_args:
        import shlex

        cmd.extend(shlex.split(extra_args))

    env = os.environ.copy()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            cwd=cwd,
            env=env,
        )
    except subprocess.TimeoutExpired:
        return f"ERROR: Claude Code subprocess timed out after {timeout_sec}s."
    except OSError as exc:
        return f"ERROR: Failed to run Claude Code: {exc}"

    out = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()
    if proc.returncode != 0:
        tail = (err or out)[:2000]
        return f"ERROR: Claude Code exited {proc.returncode}. {tail}"

    if not out:
        return f"ERROR: Empty response from Claude Code. stderr: {err[:1500]}"

    return out


def fetch_notion_page_via_claude_code(formatted_page_id: str) -> str:
    """
    Run Claude Code in print mode using a URL derived from the page UUID (legacy callers).
    Prefer fetch_notion_page_via_claude_code_url when a URL is already available.
    """
    compact = formatted_page_id.replace("-", "").strip().lower()
    url = f"https://www.notion.so/{compact}"
    return fetch_notion_page_via_claude_code_url(url)


def fetch_notion_page_via_claude_code_url(page_url: str) -> str:
    """Retrieve Notion page content via MCP using the page URL (preferred)."""
    prompt = (
        "You have access to Notion through MCP (as in your normal Claude Code setup).\n"
        f"Retrieve the full readable content of the Notion page at URL: {page_url.strip()}\n\n"
        "Output rules:\n"
        "- Return ONLY the page body as markdown (headings, lists, tables as markdown).\n"
        "- Preserve requirement identifiers exactly (RF-, RNF-, REQ-, etc.).\n"
        "- Do not wrap the answer in a markdown code fence.\n"
        "- If access fails, return a single paragraph starting with ERROR: and the reason.\n"
    )
    return run_claude_code_print(prompt, timeout_sec=None)
