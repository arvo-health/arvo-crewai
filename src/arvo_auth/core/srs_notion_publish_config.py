"""Team-scoped configuration for SRS → Notion publish crews."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

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
class SrsNotionPublishTeamConfig:
    """Paths and env vars for publishing SRS.md to Notion via Claude MCP."""

    team: str
    knowledge_dir: Path
    kickoff: SrsCrewTeamConfig
    publish_input_env: str
    publish_input_fallback_env: str | None = None
    notion_parent_url_env: str = "NOTION_SRS_PARENT_URL"
    notion_parent_id_env: str = "NOTION_SRS_PARENT_PAGE_ID"
    notion_parent_url_fallback_env: str | None = None
    notion_parent_id_fallback_env: str | None = None
    srs_workflow_subdir: str = "srs_workflow"
    notion_export_subdir: str = "notion_export"

    def default_srs_path(self, project_root: Path) -> Path:
        return (
            project_root
            / "outputs"
            / self.team
            / self.srs_workflow_subdir
            / "SRS.md"
        )

    def notion_export_dir(self, project_root: Path) -> Path:
        return project_root / "outputs" / self.team / self.notion_export_subdir

    def output_path(self, filename: str) -> str:
        return f"outputs/{self.team}/{self.notion_export_subdir}/{filename}"

    def resolve_publish_input_env(self) -> str:
        names = [self.publish_input_env]
        if self.publish_input_fallback_env:
            names.append(self.publish_input_fallback_env)
        return _env_first(*names)

    def _parent_url_env_names(self) -> tuple[str, ...]:
        names = [self.notion_parent_url_env]
        if self.notion_parent_url_fallback_env:
            names.append(self.notion_parent_url_fallback_env)
        return tuple(names)

    def _parent_id_env_names(self) -> tuple[str, ...]:
        names = [self.notion_parent_id_env]
        if self.notion_parent_id_fallback_env:
            names.append(self.notion_parent_id_fallback_env)
        return tuple(names)

    def resolve_notion_parent(self) -> tuple[NotionPageRef | None, str | None]:
        """Resolve parent page; URL env vars take precedence over legacy UUID vars."""
        return resolve_notion_page_ref(
            url_env_names=self._parent_url_env_names(),
            id_env_names=self._parent_id_env_names(),
            label="Notion SRS parent page",
        )

    def resolve_notion_parent_id(self) -> str:
        """Legacy accessor — prefer resolve_notion_parent()."""
        ref, _ = self.resolve_notion_parent()
        return ref.page_id or "" if ref else ""

    def resolve_notion_parent_url(self) -> str:
        """Primary accessor for Notion parent page."""
        ref, _ = self.resolve_notion_parent()
        return ref.url if ref else ""


ENGINEERING_NOTION_PUBLISH = SrsNotionPublishTeamConfig(
    team="engineering",
    knowledge_dir=_PKG_ROOT / "engineering" / "knowledge",
    kickoff=ENGINEERING_SRS,
    publish_input_env="ARVO_SRS_PUBLISH_INPUT",
)

COPILOT_NOTION_PUBLISH = SrsNotionPublishTeamConfig(
    team="copilot",
    knowledge_dir=_PKG_ROOT / "copilot" / "knowledge",
    kickoff=COPILOT_SRS,
    publish_input_env="ARVO_COPILOT_SRS_PUBLISH_INPUT",
    publish_input_fallback_env="ARVO_SRS_PUBLISH_INPUT",
    notion_parent_url_env="NOTION_COPILOT_SRS_PARENT_URL",
    notion_parent_url_fallback_env="NOTION_SRS_PARENT_URL",
    notion_parent_id_env="NOTION_COPILOT_SRS_PARENT_PAGE_ID",
    notion_parent_id_fallback_env="NOTION_SRS_PARENT_PAGE_ID",
)
