"""Read-only file access under backend / frontend / infra repository roots."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

_MAX_BYTES = 400_000

RepoName = Literal["backend", "frontend", "infra"]


def _project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _default_repo_root(which: RepoName) -> Path:
    workspace = _project_root().parent
    if which == "backend":
        return (workspace / "arvo-auth").resolve()
    if which == "frontend":
        return (workspace / "arvo-auth-frontend").resolve()
    # infra: same tree as backend by default (docker-compose, deploy, etc.)
    return (workspace / "arvo-auth").resolve()


def _resolve_repo_root(which: RepoName) -> Path:
    env_map = {
        "backend": "ARVO_BACKEND_REPO_ROOT",
        "frontend": "ARVO_FRONTEND_REPO_ROOT",
        "infra": "ARVO_INFRA_REPO_ROOT",
    }
    raw = os.getenv(env_map[which], "").strip()
    if raw:
        return Path(raw).expanduser().resolve()
    return _default_repo_root(which)


def _is_under_root(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


class RepoReadInput(BaseModel):
    repo: str = Field(
        ...,
        description="Which repository: backend, frontend, or infra.",
    )
    relative_path: str = Field(
        ...,
        description="File path relative to that repo root, e.g. AGENTS.md or README.md",
    )


class RepoReadTool(BaseTool):
    name: str = "read_repo_file"
    description: str = (
        "Read a text file from the Arvo backend (Go), frontend (Next.js), or infra "
        "repository. Use for AGENTS.md, README, go.mod, package.json, docker-compose.yml, "
        "and representative source paths. Repo roots come from environment or default "
        "sibling folders arvo-auth / arvo-auth-frontend."
    )
    args_schema: Type[BaseModel] = RepoReadInput

    def _run(self, repo: str, relative_path: str) -> str:
        which = repo.strip().lower()
        if which not in ("backend", "frontend", "infra"):
            return "Invalid repo: use backend, frontend, or infra."

        root = _resolve_repo_root(which)  # type: ignore[arg-type]
        if not root.is_dir():
            return f"Repository root is not a directory: {root}. Set ARVO_*_REPO_ROOT."

        cleaned = relative_path.strip().lstrip("/")
        if not cleaned or ".." in Path(cleaned).parts:
            return "Invalid path: no '..' components."

        target = (root / cleaned).resolve()
        if not _is_under_root(target, root):
            return "Path escapes repository root."

        if not target.is_file():
            return f"Not a file or missing: {repo}/{cleaned}"

        if target.stat().st_size > _MAX_BYTES:
            return f"File too large (max {_MAX_BYTES} bytes); read a smaller file."

        try:
            return target.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            return f"Read error: {exc}"
