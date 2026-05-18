"""Shared helpers for invoking the GitHub CLI (`gh`) from CrewAI tools."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import Any

_MAX_OUTPUT_CHARS = 48_000
_DEFAULT_TIMEOUT_SEC = 90


def gh_binary() -> str | None:
    path = os.getenv("GH_PATH", "").strip() or shutil.which("gh")
    return path or None


def run_gh(
    args: list[str],
    *,
    repo: str | None = None,
    repo_style: str = "flag",
    timeout_sec: int = _DEFAULT_TIMEOUT_SEC,
) -> str:
    """Run `gh` with the given subcommand args; return stdout or an error string."""
    binary = gh_binary()
    if not binary:
        return (
            "ERROR: GitHub CLI (`gh`) not found. Install it and run `gh auth login`, "
            "or set GH_PATH to the binary location."
        )

    cleaned_repo = repo.strip() if repo else ""
    cmd: list[str] = [binary]

    if cleaned_repo and repo_style == "positional":
        # e.g. gh repo view [<repository>] — repo is a positional arg after "view"
        if len(args) >= 2:
            cmd.extend([args[0], args[1], cleaned_repo, *args[2:]])
        else:
            cmd.extend([*args, cleaned_repo])
    else:
        cmd.extend(args)
        if cleaned_repo and repo_style == "flag":
            cmd.extend(["-R", cleaned_repo])

    env = os.environ.copy()
    env.setdefault("GH_PAGER", "cat")
    env.setdefault("PAGER", "cat")

    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            env=env,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return f"ERROR: `gh` timed out after {timeout_sec}s (command: {' '.join(args[:4])})."
    except OSError as exc:
        return f"ERROR: failed to run `gh`: {exc}"

    stdout = (completed.stdout or "").strip()
    stderr = (completed.stderr or "").strip()

    if completed.returncode != 0:
        detail = stderr or stdout or f"exit code {completed.returncode}"
        return f"ERROR: `gh {' '.join(args[:6])}` failed: {detail[:4000]}"

    if not stdout:
        return "(no output)"

    if len(stdout) > _MAX_OUTPUT_CHARS:
        return (
            stdout[:_MAX_OUTPUT_CHARS]
            + f"\n\n... [truncated; total {len(stdout)} characters]"
        )

    return stdout


def format_json_output(raw: str) -> str:
    """Pretty-print JSON from `gh --json` when possible."""
    try:
        data: Any = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    return json.dumps(data, indent=2, ensure_ascii=False)
