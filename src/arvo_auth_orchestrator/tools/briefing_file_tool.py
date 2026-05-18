"""Read markdown briefing or rule files from the project knowledge/ directory only."""

from __future__ import annotations

from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

_MAX_BYTES = 256_000


def _knowledge_root() -> Path:
    # src/arvo_auth_orchestrator/tools/ -> project root parents[3]
    return Path(__file__).resolve().parents[3] / "knowledge"


class BriefingFileReadInput(BaseModel):
    relative_path: str = Field(
        ...,
        description="Path under the project knowledge/ folder, e.g. srs_authoring_rules.md",
    )


class BriefingFileReadTool(BaseTool):
    name: str = "read_briefing_markdown"
    description: str = (
        "Load a .md file from this project's knowledge/ directory (context, SRS rules, "
        "phase notes). Use only the filename or a subpath inside knowledge/."
    )
    args_schema: Type[BaseModel] = BriefingFileReadInput

    def _run(self, relative_path: str) -> str:
        root = _knowledge_root()
        if not root.is_dir():
            return f"knowledge/ directory missing at {root}"

        cleaned = relative_path.strip().lstrip("/")
        if not cleaned or ".." in Path(cleaned).parts:
            return "Invalid path: stay inside knowledge/ without '..'."

        target = (root / cleaned).resolve()
        try:
            target.relative_to(root.resolve())
        except ValueError:
            return "Path escapes knowledge/ directory."

        if not target.is_file():
            return f"File not found: knowledge/{cleaned}"

        if target.stat().st_size > _MAX_BYTES:
            return f"File too large; max {_MAX_BYTES} bytes."

        return target.read_text(encoding="utf-8", errors="replace")
