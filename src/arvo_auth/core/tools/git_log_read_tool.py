"""Read-only `git log` from a repository configured via ARVO_REPO_<NAME>."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

_VALID_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
_DEFAULT_MAX_COMMITS = 20
_HARD_CAP_COMMITS = 200
_DEFAULT_TIMEOUT_SEC = 30


def _env_var_for(name: str) -> str:
    return f"ARVO_REPO_{name.upper()}"


def _resolve_repo_root(name: str) -> Path | None:
    raw = os.getenv(_env_var_for(name), "").strip()
    if not raw:
        return None
    return Path(raw).expanduser().resolve()


def _is_under_root(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


class GitLogReadInput(BaseModel):
    repo: str = Field(
        ...,
        description=(
            "Logical repo name resolved from env ARVO_REPO_<NAME> "
            "(e.g. 'intelligence', 'tea_analyzer', 'roots')."
        ),
    )
    relative_path: str = Field(
        default="",
        description=(
            "Optional sub-path inside the repo to restrict the log to "
            "(e.g. 'services/doc-quality'). Empty = whole repo."
        ),
    )
    max_commits: int = Field(
        default=_DEFAULT_MAX_COMMITS,
        description=(
            f"How many recent commits to return. Default {_DEFAULT_MAX_COMMITS}, "
            f"hard cap {_HARD_CAP_COMMITS}."
        ),
    )


class GitLogReadTool(BaseTool):
    name: str = "read_git_log"
    description: str = (
        "Read recent git log entries from a configured repository (read-only). "
        "Returns commit hash, author, relative date, and subject for the N most "
        "recent commits, optionally scoped to a sub-path. Use to detect when a "
        "service was last touched, who has been editing it, and whether it has "
        "been quiet (a strong lifecycle signal for handover documentation)."
    )
    args_schema: Type[BaseModel] = GitLogReadInput

    def _run(
        self, repo: str, relative_path: str = "", max_commits: int = _DEFAULT_MAX_COMMITS
    ) -> str:
        name = repo.strip()
        if not name:
            return "ERROR: repo is empty."
        if not _VALID_NAME.match(name):
            return (
                f"ERROR: invalid repo name '{name}'. "
                "Use letters, digits and underscore; must start with a letter."
            )

        root = _resolve_repo_root(name)
        if root is None:
            return (
                f"ERROR: env var {_env_var_for(name)} is not set. "
                "Define it in .env to point at the repo root."
            )
        if not root.is_dir():
            return f"ERROR: repo root for '{name}' is not a directory: {root}."

        n = max(1, min(int(max_commits), _HARD_CAP_COMMITS))

        path_arg: list[str] = []
        if relative_path.strip():
            cleaned = relative_path.strip().lstrip("/")
            if ".." in Path(cleaned).parts:
                return "ERROR: relative_path must not contain '..'."
            target = (root / cleaned).resolve()
            if not _is_under_root(target, root):
                return "ERROR: relative_path escapes repo root."
            if not target.exists():
                return f"ERROR: path does not exist: {name}/{cleaned}"
            path_arg = ["--", cleaned]

        git = shutil.which("git")
        if not git:
            return "ERROR: `git` not found in PATH."

        cmd = [
            git,
            "log",
            f"-n{n}",
            "--no-color",
            "--date=relative",
            "--pretty=format:%h | %ad | %an | %s",
            *path_arg,
        ]

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=root,
                timeout=_DEFAULT_TIMEOUT_SEC,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return f"ERROR: git log timed out after {_DEFAULT_TIMEOUT_SEC}s."
        except OSError as exc:
            return f"ERROR: failed to run git: {exc}"

        if proc.returncode != 0:
            err = (proc.stderr or "").strip()[:1000]
            return f"ERROR: git log exited {proc.returncode}: {err or '(no stderr)'}"

        out = (proc.stdout or "").strip()
        if not out:
            scope = f" in {relative_path}" if relative_path.strip() else ""
            return f"(no commits found{scope})"
        return out
