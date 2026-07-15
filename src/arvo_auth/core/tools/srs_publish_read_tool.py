"""Read the SRS.md file that will be published to Notion (team-scoped workflow)."""

from __future__ import annotations

from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from arvo_auth.core.srs_notion_publish_config import (
    ENGINEERING_NOTION_PUBLISH,
    SrsNotionPublishTeamConfig,
)
from arvo_auth.core.srs_publish_paths import resolve_srs_publish_path


class SrsPublishReadInput(BaseModel):
    dummy: str = Field(
        default="",
        description="Unused; call with empty arguments.",
    )


class SrsPublishReadTool(BaseTool):
    name: str = "read_srs_for_notion_publish"
    description: str = (
        "Load the full SRS.md for the Notion publish workflow. Uses the team publish "
        "input env var or defaults to outputs/<team>/srs_workflow/SRS.md under this project."
    )
    args_schema: Type[BaseModel] = SrsPublishReadInput
    publish_config: SrsNotionPublishTeamConfig = ENGINEERING_NOTION_PUBLISH

    def _run(self, dummy: str = "") -> str:
        path, err = resolve_srs_publish_path(self.publish_config)
        if err:
            return err
        assert path is not None
        return path.read_text(encoding="utf-8", errors="replace")
