"""Team-scoped configuration for SRS → Linear issue creation crews."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from arvo_auth.core.linear_project_ref import LinearProjectRef, resolve_linear_project_ref
from arvo_auth.core.notion_page_ref import NotionPageRef, resolve_notion_page_ref
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
    srs_notion_page_url_env: str
    linear_team_key_env: str
    linear_project_url_env: str
    srs_notion_page_url_fallback_env: str | None = None
    srs_notion_page_id_fallback_envs: tuple[str, ...] = ()
    linear_team_key_fallback_env: str | None = None
    linear_project_url_fallback_env: str | None = None
    linear_project_legacy_envs: tuple[str, ...] = ()
    output_subdir: str = "linear_tasks_creation"

    def output_dir(self, project_root: Path) -> Path:
        return project_root / "outputs" / self.team / self.output_subdir

    def output_path(self, filename: str) -> str:
        return f"outputs/{self.team}/{self.output_subdir}/{filename}"

    def _srs_url_env_names(self) -> tuple[str, ...]:
        names = [self.srs_notion_page_url_env]
        if self.srs_notion_page_url_fallback_env:
            names.append(self.srs_notion_page_url_fallback_env)
        return tuple(names)

    def _srs_id_env_names(self) -> tuple[str, ...]:
        return self.srs_notion_page_id_fallback_envs

    def _linear_project_url_env_names(self) -> tuple[str, ...]:
        names = [self.linear_project_url_env]
        if self.linear_project_url_fallback_env:
            names.append(self.linear_project_url_fallback_env)
        return tuple(names)

    def resolve_srs_notion_page(self) -> tuple[NotionPageRef | None, str | None]:
        """Resolve SRS Dashboard page; URL env vars take precedence over legacy UUID vars."""
        return resolve_notion_page_ref(
            url_env_names=self._srs_url_env_names(),
            id_env_names=self._srs_id_env_names(),
            label="SRS Notion page",
        )

    def resolve_srs_notion_page_url(self) -> str:
        ref, _ = self.resolve_srs_notion_page()
        return ref.url if ref else ""

    def resolve_linear_team_key(self) -> str:
        names = [self.linear_team_key_env]
        if self.linear_team_key_fallback_env:
            names.append(self.linear_team_key_fallback_env)
        return _env_first(*names)

    def resolve_linear_project(self) -> tuple[LinearProjectRef | None, str | None]:
        """Resolve optional Linear project; URL env vars take precedence over legacy vars."""
        return resolve_linear_project_ref(
            url_env_names=self._linear_project_url_env_names(),
            legacy_env_names=self.linear_project_legacy_envs,
        )


ENGINEERING_LINEAR_TASKS = LinearTasksTeamConfig(
    team="engineering",
    knowledge_dir=_PKG_ROOT / "engineering" / "knowledge",
    kickoff=ENGINEERING_SRS,
    srs_notion_page_url_env="ARVO_SRS_NOTION_PAGE_URL",
    srs_notion_page_id_fallback_envs=("ARVO_SRS_NOTION_PAGE_ID",),
    linear_team_key_env="ARVO_LINEAR_TEAM_KEY",
    linear_project_url_env="ARVO_LINEAR_PROJECT_URL",
    linear_project_legacy_envs=(
        "ARVO_LINEAR_PROJECT_ID",
        "ARVO_LINEAR_PROJECT_NAME",
    ),
)

COPILOT_LINEAR_TASKS = LinearTasksTeamConfig(
    team="copilot",
    knowledge_dir=_PKG_ROOT / "copilot" / "knowledge",
    kickoff=COPILOT_SRS,
    srs_notion_page_url_env="ARVO_COPILOT_SRS_NOTION_PAGE_URL",
    srs_notion_page_url_fallback_env="ARVO_SRS_NOTION_PAGE_URL",
    srs_notion_page_id_fallback_envs=(
        "ARVO_COPILOT_SRS_NOTION_PAGE_ID",
        "ARVO_SRS_NOTION_PAGE_ID",
    ),
    linear_team_key_env="ARVO_COPILOT_LINEAR_TEAM_KEY",
    linear_team_key_fallback_env="ARVO_LINEAR_TEAM_KEY",
    linear_project_url_env="ARVO_COPILOT_LINEAR_PROJECT_URL",
    linear_project_url_fallback_env="ARVO_LINEAR_PROJECT_URL",
    linear_project_legacy_envs=(
        "ARVO_COPILOT_LINEAR_PROJECT_ID",
        "ARVO_COPILOT_LINEAR_PROJECT_NAME",
        "ARVO_LINEAR_PROJECT_ID",
        "ARVO_LINEAR_PROJECT_NAME",
    ),
)
