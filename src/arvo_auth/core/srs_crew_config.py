"""Team-scoped configuration for SRS author crews."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

_PKG_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class SrsCrewTeamConfig:
    """Namespace and env-prefix settings for an SRS author crew instance."""

    team: str
    knowledge_dir: Path
    default_project_name: str
    env_prefix: str
    output_subdir: str = "srs_workflow"
    fallback_env_prefix: str | None = None
    replay_task_id_env: str | None = None

    def output_dir(self, project_root: Path) -> Path:
        return project_root / "outputs" / self.team / self.output_subdir

    def output_path(self, filename: str) -> str:
        return f"outputs/{self.team}/{self.output_subdir}/{filename}"


ENGINEERING_SRS = SrsCrewTeamConfig(
    team="engineering",
    knowledge_dir=_PKG_ROOT / "engineering" / "knowledge",
    default_project_name="Arvo authorization",
    env_prefix="ARVO_SRS",
    replay_task_id_env="ARVO_SRS_REPLAY_TASK_ID",
)

COPILOT_SRS = SrsCrewTeamConfig(
    team="copilot",
    knowledge_dir=_PKG_ROOT / "copilot" / "knowledge",
    default_project_name="Arvo Copilot",
    env_prefix="ARVO_COPILOT_SRS",
    fallback_env_prefix="ARVO_SRS",
    replay_task_id_env="ARVO_COPILOT_SRS_REPLAY_TASK_ID",
)
