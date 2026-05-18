"""Read artefacts produced by the SRS → Notion publish crew (read-only allowlist)."""

from __future__ import annotations

from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

_ALLOWED = frozenset(
    {
        "publish_plan.md",
        "publish_execution_log.md",
        "publish_completeness_review.md",
    }
)
_MAX_BYTES = 600_000


def _notion_export_dir() -> Path:
    return Path(__file__).resolve().parents[4] / "outputs" / "engineering" / "notion_export"


class NotionPublishArtifactReadInput(BaseModel):
    filename: str = Field(
        ...,
        description=(
            "Artefact name under outputs/notion_export/. Allowed values: "
            "publish_plan.md, publish_execution_log.md, publish_completeness_review.md."
        ),
    )


class NotionPublishArtifactReadTool(BaseTool):
    name: str = "read_notion_publish_artifact"
    description: str = (
        "Load a previously written Notion publish artefact from outputs/notion_export/. "
        "Use to inspect the existing Notion page tree (plan, execution log with URLs, "
        "completeness review) before planning a diff."
    )
    args_schema: Type[BaseModel] = NotionPublishArtifactReadInput

    def _run(self, filename: str) -> str:
        name = (filename or "").strip()
        if name not in _ALLOWED:
            return f"Unknown artefact. Allowed: {', '.join(sorted(_ALLOWED))}"

        path = _notion_export_dir() / name
        if not path.is_file():
            return (
                f"File not found yet: {path}. Run `uv run run_notion_publish` first "
                "so the publish plan and execution log are written to disk."
            )

        if path.stat().st_size > _MAX_BYTES:
            return f"File too large (max {_MAX_BYTES} bytes)."

        return path.read_text(encoding="utf-8", errors="replace")
