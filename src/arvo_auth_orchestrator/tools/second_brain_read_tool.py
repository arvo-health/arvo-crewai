"""Read-only access to the Arvo second-brain knowledge tree (markdown, etc.)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

_MAX_BYTES = 512_000


def _resolve_second_brain_root() -> Path:
    raw = os.getenv("ARVO_SECOND_BRAIN_ROOT", "").strip()
    if raw:
        return Path(raw).expanduser().resolve()
    # This file: src/arvo_auth_orchestrator/tools/... → package root is parents[2], repo root is parents[3]
    project_root = Path(__file__).resolve().parents[3]
    sibling = project_root.parent / "second-brain"
    if sibling.is_dir():
        return sibling.resolve()
    return (project_root / "knowledge").resolve()


def _is_under_root(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


class SecondBrainReadInput(BaseModel):
    """Path relative to the second-brain root (no leading slash)."""

    relative_path: str = Field(
        ...,
        description="File path relative to second-brain root, e.g. plans/backend/foo/plano.md",
    )


class SecondBrainReadTool(BaseTool):
    name: str = "read_second_brain_file"
    description: str = (
        "Read a text file from the Arvo second-brain knowledge repository. "
        "Use relative paths from the repository root (markdown plans, history, integrations). "
        "Returns file contents or an error message if the path is invalid or too large."
    )
    args_schema: Type[BaseModel] = SecondBrainReadInput

    def _run(self, relative_path: str) -> str:
        root = _resolve_second_brain_root()
        if not root.is_dir():
            return f"Second-brain root is not a directory: {root}. Set ARVO_SECOND_BRAIN_ROOT."

        cleaned = relative_path.strip().lstrip("/")
        if not cleaned or ".." in Path(cleaned).parts:
            return "Invalid path: use a relative path without '..' components."

        target = (root / cleaned).resolve()
        if not _is_under_root(target, root):
            return "Path escapes second-brain root; request denied."

        if not target.is_file():
            return f"Not a file or missing: {cleaned}"

        size = target.stat().st_size
        if size > _MAX_BYTES:
            return f"File too large ({size} bytes); max {_MAX_BYTES}. Read a smaller fragment or another file."

        try:
            return target.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            return f"Read error: {exc}"
