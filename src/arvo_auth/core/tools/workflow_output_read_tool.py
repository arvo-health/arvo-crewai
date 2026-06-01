"""Re-read intermediate workflow markdown from outputs/<team>/<workflow_dir>/."""

from __future__ import annotations

from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

_ALLOWED_BY_DIR: dict[str, frozenset[str]] = {
    "srs_workflow": frozenset(
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
    ),
    "frontend_branch_mapping": frozenset(
        {
            "01_github_delta.md",
            "02_code_analysis.md",
            "branch_mapping.md",
        }
    ),
    "linear_tasks_creation": frozenset(
        {
            "01_srs_content.md",
            "02_issues_draft.json",
            "03_publish_log.md",
        }
    ),
}
_MAX_BYTES = 600_000


def _project_outputs_root() -> Path:
    return Path(__file__).resolve().parents[4] / "outputs"


class WorkflowOutputReadInput(BaseModel):
    filename: str = Field(
        ...,
        description="Artifact file name only (e.g. overview.md or 01_github_delta.md).",
    )
    workflow_dir: str = Field(
        default="srs_workflow",
        description=(
            "Subfolder under outputs/<team>/: srs_workflow (default), "
            "frontend_branch_mapping, or linear_tasks_creation."
        ),
    )


class WorkflowOutputReadTool(BaseTool):
    name: str = "read_workflow_artifact"
    description: str = (
        "Load a markdown artifact from outputs/<team>/. Use workflow_dir=srs_workflow "
        "for SRS steps, workflow_dir=frontend_branch_mapping for branch mapping artefacts, "
        "or workflow_dir=linear_tasks_creation for 01_srs_content.md, "
        "02_issues_draft.json, and 03_publish_log.md."
    )
    args_schema: Type[BaseModel] = WorkflowOutputReadInput
    outputs_team: str = "engineering"

    def _outputs_root(self) -> Path:
        return _project_outputs_root() / self.outputs_team

    def _run(self, filename: str, workflow_dir: str = "srs_workflow") -> str:
        subdir = workflow_dir.strip() or "srs_workflow"
        allowed = _ALLOWED_BY_DIR.get(subdir)
        if not allowed:
            known = ", ".join(sorted(_ALLOWED_BY_DIR))
            return f"Unknown workflow_dir {workflow_dir!r}. Use one of: {known}"

        name = filename.strip()
        if name not in allowed:
            return f"Unknown artifact for {subdir}. Allowed: {', '.join(sorted(allowed))}"

        path = self._outputs_root() / subdir / name
        if not path.is_file():
            return f"File not found yet: {path}. Run earlier workflow steps first."

        if path.stat().st_size > _MAX_BYTES:
            return f"File too large (max {_MAX_BYTES} bytes)."

        return path.read_text(encoding="utf-8", errors="replace")
