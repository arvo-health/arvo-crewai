"""Team-scoped configuration for SRS → Linear issue creation crews."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from arvo_auth.core.srs_crew_config import (
    COPILOT_SRS,
    ENGINEERING_SRS,
    SrsCrewTeamConfig,
    _PKG_ROOT,
)


def _env_first(*names: str) -> str:
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""


@dataclass(frozen=True)
class LinearTasksTeamConfig:
    """Paths and env vars for decomposing SRS Notion pages into Linear issues."""

    team: str
    knowledge_dir: Path
    kickoff: SrsCrewTeamConfig
    srs_notion_page_id_env: str
    linear_team_key_env: str
    srs_notion_page_id_fallback_env: str | None = None
    linear_team_key_fallback_env: str | None = None
    output_subdir: str = "linear_tasks_creation"

    def output_dir(self, project_root: Path) -> Path:
        return project_root / "outputs" / self.team / self.output_subdir

    def output_path(self, filename: str) -> str:
        return f"outputs/{self.team}/{self.output_subdir}/{filename}"

    def resolve_srs_notion_page_id(self) -> str:
        names = [self.srs_notion_page_id_env]
        if self.srs_notion_page_id_fallback_env:
            names.append(self.srs_notion_page_id_fallback_env)
        return _env_first(*names)

    def resolve_linear_team_key(self) -> str:
        names = [self.linear_team_key_env]
        if self.linear_team_key_fallback_env:
            names.append(self.linear_team_key_fallback_env)
        return _env_first(*names)


ENGINEERING_LINEAR_TASKS = LinearTasksTeamConfig(
    team="engineering",
    knowledge_dir=_PKG_ROOT / "engineering" / "knowledge",
    kickoff=ENGINEERING_SRS,
    srs_notion_page_id_env="ARVO_SRS_NOTION_PAGE_ID",
    linear_team_key_env="ARVO_LINEAR_TEAM_KEY",
)

COPILOT_LINEAR_TASKS = LinearTasksTeamConfig(
    team="copilot",
    knowledge_dir=_PKG_ROOT / "copilot" / "knowledge",
    kickoff=COPILOT_SRS,
    srs_notion_page_id_env="ARVO_COPILOT_SRS_NOTION_PAGE_ID",
    srs_notion_page_id_fallback_env="ARVO_SRS_NOTION_PAGE_ID",
    linear_team_key_env="ARVO_COPILOT_LINEAR_TEAM_KEY",
    linear_team_key_fallback_env="ARVO_LINEAR_TEAM_KEY",
)
