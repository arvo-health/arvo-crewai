"""Read markdown briefing or rule files from any team's knowledge/ directory."""

from __future__ import annotations

from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

_MAX_BYTES = 256_000


def _package_root() -> Path:
    # src/arvo_auth/core/tools/ -> src/arvo_auth/ is parents[2]
    return Path(__file__).resolve().parents[2]


def _knowledge_roots() -> list[Path]:
    """All team knowledge/ dirs under src/arvo_auth/<team>/knowledge/.

    Multi-team: a file is resolved against whichever team owns it (engineering,
    data_science, etc.). Engineering is searched first for backward compatibility.
    """
    pkg = _package_root()
    roots: list[Path] = []
    eng = pkg / "engineering" / "knowledge"
    if eng.is_dir():
        roots.append(eng)
    for kn in sorted(pkg.glob("*/knowledge")):
        if kn.is_dir() and kn != eng:
            roots.append(kn)
    return roots


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
        roots = _knowledge_roots()
        if not roots:
            return f"No knowledge/ directory found under {_package_root()}"

        cleaned = relative_path.strip().lstrip("/")
        if not cleaned or ".." in Path(cleaned).parts:
            return "Invalid path: stay inside knowledge/ without '..'."

        searched: list[str] = []
        for root in roots:
            target = (root / cleaned).resolve()
            try:
                target.relative_to(root.resolve())
            except ValueError:
                return "Path escapes knowledge/ directory."
            searched.append(root.parent.name)
            if target.is_file():
                if target.stat().st_size > _MAX_BYTES:
                    return f"File too large; max {_MAX_BYTES} bytes."
                return target.read_text(encoding="utf-8", errors="replace")

        return (
            f"File not found: knowledge/{cleaned} "
            f"(searched teams: {', '.join(searched)})"
        )
