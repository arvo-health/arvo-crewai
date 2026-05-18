"""Read the SRS.md file that will be published to Notion (independent workflow)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

_MAX_BYTES = 1_500_000


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve_srs_path() -> tuple[Path | None, str | None]:
    root = _project_root()
    raw = os.getenv("ARVO_SRS_PUBLISH_INPUT", "").strip()
    if raw:
        p = Path(raw)
        candidate = (
            p.expanduser().resolve()
            if p.is_absolute()
            else (root / p).resolve()
        )
    else:
        candidate = (root / "outputs" / "srs_workflow" / "SRS.md").resolve()

    if not candidate.is_file():
        return None, f"SRS file not found: {candidate}"

    if candidate.suffix.lower() != ".md":
        return None, "Refusing: path must be a .md file."

    if candidate.stat().st_size > _MAX_BYTES:
        return None, f"File too large (max {_MAX_BYTES} bytes)."

    if not raw:
        try:
            candidate.relative_to(root.resolve())
        except ValueError:
            return None, "Default SRS path is outside the project tree."
    else:
        if not p.is_absolute():
            try:
                candidate.relative_to(root.resolve())
            except ValueError:
                return None, "Relative ARVO_SRS_PUBLISH_INPUT must stay under the project root."

    return candidate, None


class SrsPublishReadInput(BaseModel):
    dummy: str = Field(
        default="",
        description="Unused; call with empty arguments.",
    )


class SrsPublishReadTool(BaseTool):
    name: str = "read_srs_for_notion_publish"
    description: str = (
        "Load the full SRS.md for the Notion publish workflow. Uses ARVO_SRS_PUBLISH_INPUT "
        "or defaults to outputs/srs_workflow/SRS.md under this project."
    )
    args_schema: Type[BaseModel] = SrsPublishReadInput

    def _run(self, dummy: str = "") -> str:
        path, err = _resolve_srs_path()
        if err:
            return err
        assert path is not None
        return path.read_text(encoding="utf-8", errors="replace")
