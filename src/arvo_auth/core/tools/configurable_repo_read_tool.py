"""Read-only access to arbitrary external repos, resolved from ARVO_REPO_<NAME> env vars."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

_MAX_BYTES = 400_000
_VALID_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


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


class ConfigurableRepoReadInput(BaseModel):
    repo: str = Field(
        ...,
        description=(
            "Logical repo name (case-insensitive) resolved from env var ARVO_REPO_<NAME>. "
            "Examples: 'intelligence' → ARVO_REPO_INTELLIGENCE, "
            "'tea_analyzer' → ARVO_REPO_TEA_ANALYZER, 'roots' → ARVO_REPO_ROOTS."
        ),
    )
    relative_path: str = Field(
        ...,
        description=(
            "File path relative to the repo root (no leading slash, no '..'). "
            "Example: 'services/doc-extractor/README.md'."
        ),
    )


class ConfigurableRepoReadTool(BaseTool):
    name: str = "read_repo_file"
    description: str = (
        "Read a text file from a repository configured via env vars. The repo is "
        "identified by a logical name; its absolute path comes from ARVO_REPO_<NAME>. "
        "Useful when an agent needs to inspect multiple sibling repositories (services, "
        "pipelines, downstream workflows) without hard-coding paths."
    )
    args_schema: Type[BaseModel] = ConfigurableRepoReadInput

    def _run(self, repo: str, relative_path: str) -> str:
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
                f"Define it in .env to point at the repo root."
            )
        if not root.is_dir():
            return (
                f"ERROR: repo root for '{name}' is not a directory: {root}. "
                f"Check {_env_var_for(name)}."
            )

        cleaned = relative_path.strip().lstrip("/")
        if not cleaned:
            return "ERROR: relative_path is empty."
        if ".." in Path(cleaned).parts:
            return "ERROR: relative_path must not contain '..'."

        target = (root / cleaned).resolve()
        if not _is_under_root(target, root):
            return f"ERROR: path escapes repo root '{name}'."

        if not target.is_file():
            return f"ERROR: not a file or missing: {name}/{cleaned}"

        size = target.stat().st_size
        if size > _MAX_BYTES:
            return (
                f"ERROR: file too large ({size} bytes; max {_MAX_BYTES}). "
                "Read a smaller file or a fragment via another tool."
            )

        try:
            return target.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            return f"ERROR: read failed: {exc}"
