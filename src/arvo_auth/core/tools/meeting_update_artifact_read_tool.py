"""Read intermediate artefacts produced by the SRS meeting-update crews."""

from __future__ import annotations

from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

_ALLOWED = frozenset(
    {
        "srs_changes_manifest.md",
        "notion_comment_suggestions.md",
        "notion_changes_diff.md",
        "diff_revision_feedback.md",
        "apply_execution_log.md",
        "versions_update_log.md",
    }
)
_MAX_BYTES = 600_000


def _meeting_update_dir() -> Path:
    return Path(__file__).resolve().parents[4] / "outputs" / "engineering" / "srs_meeting_update"


class MeetingUpdateArtifactReadInput(BaseModel):
    filename: str = Field(
        ...,
        description=(
            "Artefact name under outputs/srs_meeting_update/. Allowed values: "
            "srs_changes_manifest.md, notion_comment_suggestions.md, notion_changes_diff.md, "
            "diff_revision_feedback.md, apply_execution_log.md, versions_update_log.md."
        ),
    )


class MeetingUpdateArtifactReadTool(BaseTool):
    name: str = "read_meeting_update_artifact"
    description: str = (
        "Load a previously written meeting-update artefact from "
        "outputs/srs_meeting_update/. Use between tasks to read manifest, diff, or "
        "human feedback files. Only a closed allowlist is permitted."
    )
    args_schema: Type[BaseModel] = MeetingUpdateArtifactReadInput

    def _run(self, filename: str) -> str:
        name = (filename or "").strip()
        if name not in _ALLOWED:
            return f"Unknown artefact. Allowed: {', '.join(sorted(_ALLOWED))}"

        path = _meeting_update_dir() / name
        if not path.is_file():
            return (
                f"File not found yet: {path}. Run the prior meeting-update task first "
                "or check that the crew kickoff has completed it."
            )

        if path.stat().st_size > _MAX_BYTES:
            return f"File too large (max {_MAX_BYTES} bytes)."

        return path.read_text(encoding="utf-8", errors="replace")
