"""Re-read intermediate SRS workflow markdown from outputs/srs_workflow/."""

from __future__ import annotations

from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

_ALLOWED = frozenset(
    {
        "step_01_ingest_memory.md",
        "overview.md",
        "product_research_notes.md",
        "product.md",
        "repo_analysis.md",
        "backend.md",
        "frontend.md",
        "infra.md",
        "gaps_and_open_questions.md",
        "SRS.md",
    }
)
_MAX_BYTES = 600_000


def _workflow_dir() -> Path:
    return Path(__file__).resolve().parents[4] / "outputs" / "engineering" / "srs_workflow"


class WorkflowOutputReadInput(BaseModel):
    filename: str = Field(
        ...,
        description="Artifact name under outputs/srs_workflow/, e.g. overview.md or product.md",
    )


class WorkflowOutputReadTool(BaseTool):
    name: str = "read_workflow_artifact"
    description: str = (
        "Load a previously written workflow markdown file from outputs/srs_workflow/. "
        "Use between workflow steps to read the prior step output from outputs/srs_workflow/, "
        "or during final SRS authoring when you need the full artifact text."
    )
    args_schema: Type[BaseModel] = WorkflowOutputReadInput

    def _run(self, filename: str) -> str:
        name = filename.strip()
        if name not in _ALLOWED:
            return f"Unknown artifact. Allowed: {', '.join(sorted(_ALLOWED))}"

        path = _workflow_dir() / name
        if not path.is_file():
            return f"File not found yet: {path}. Run earlier workflow steps first."

        if path.stat().st_size > _MAX_BYTES:
            return f"File too large (max {_MAX_BYTES} bytes)."

        return path.read_text(encoding="utf-8", errors="replace")
