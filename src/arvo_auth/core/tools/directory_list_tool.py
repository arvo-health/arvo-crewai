"""Read-only directory listing in a repository configured via ARVO_REPO_<NAME>."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

_VALID_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
_DEFAULT_MAX_DEPTH = 3
_HARD_CAP_DEPTH = 6
_DEFAULT_MAX_ENTRIES = 500
_HARD_CAP_ENTRIES = 2000

_SKIP_DIR_NAMES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "htmlcov",
    "dist",
    "build",
    ".egg-info",
}


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


def _is_skipped(name: str) -> bool:
    if name in _SKIP_DIR_NAMES:
        return True
    if name.endswith(".egg-info"):
        return True
    return False


class DirectoryListInput(BaseModel):
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
            "Optional sub-path to list inside the repo (e.g. 'services/doc-quality'). "
            "Empty = repo root."
        ),
    )
    max_depth: int = Field(
        default=_DEFAULT_MAX_DEPTH,
        description=(
            f"How deep to recurse. Default {_DEFAULT_MAX_DEPTH}, hard cap {_HARD_CAP_DEPTH}."
        ),
    )


class DirectoryListTool(BaseTool):
    name: str = "list_repo_directory"
    description: str = (
        "List files and directories inside a configured repository (read-only, "
        "depth-limited). Skips noise (.git, .venv, __pycache__, node_modules, "
        "caches). Use to discover what a service contains before deciding which "
        "specific files to read with read_repo_file."
    )
    args_schema: Type[BaseModel] = DirectoryListInput

    def _run(
        self,
        repo: str,
        relative_path: str = "",
        max_depth: int = _DEFAULT_MAX_DEPTH,
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

        cleaned = relative_path.strip().lstrip("/")
        if ".." in Path(cleaned).parts:
            return "ERROR: relative_path must not contain '..'."

        start = (root / cleaned).resolve() if cleaned else root
        if not _is_under_root(start, root):
            return "ERROR: relative_path escapes repo root."
        if not start.exists():
            return f"ERROR: path does not exist: {name}/{cleaned}"
        if not start.is_dir():
            return f"ERROR: path is not a directory: {name}/{cleaned}"

        depth = max(1, min(int(max_depth), _HARD_CAP_DEPTH))
        lines: list[str] = []
        entry_count = 0
        truncated = False

        def _walk(d: Path, current_depth: int, prefix: str) -> None:
            nonlocal entry_count, truncated
            if truncated or current_depth > depth:
                return
            try:
                entries = sorted(
                    os.scandir(d),
                    key=lambda e: (not e.is_dir(follow_symlinks=False), e.name.lower()),
                )
            except OSError as exc:
                lines.append(f"{prefix}[error reading {d.name}: {exc}]")
                return

            for entry in entries:
                if truncated:
                    return
                if entry.name.startswith(".") and entry.name != ".env.example":
                    if entry.is_dir(follow_symlinks=False):
                        continue
                if entry.is_dir(follow_symlinks=False) and _is_skipped(entry.name):
                    continue

                entry_count += 1
                if entry_count > _DEFAULT_MAX_ENTRIES:
                    truncated = True
                    lines.append(f"{prefix}... [truncated at {_DEFAULT_MAX_ENTRIES} entries]")
                    return

                marker = "/" if entry.is_dir(follow_symlinks=False) else ""
                lines.append(f"{prefix}{entry.name}{marker}")
                if entry.is_dir(follow_symlinks=False) and current_depth < depth:
                    _walk(Path(entry.path), current_depth + 1, prefix + "  ")

        header = f"{name}/{cleaned}" if cleaned else f"{name}/"
        lines.append(f"{header.rstrip('/')}/")
        _walk(start, 1, "  ")
        return "\n".join(lines)
