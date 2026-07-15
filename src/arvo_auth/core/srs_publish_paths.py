"""Resolve SRS publish paths per team."""

from __future__ import annotations

from pathlib import Path

from arvo_auth.core.srs_notion_publish_config import SrsNotionPublishTeamConfig

_MAX_BYTES = 1_500_000


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def resolve_srs_publish_path_legacy() -> tuple[Path | None, str | None]:
    """Engineering default SRS path (backward compatibility for meeting-update tools)."""
    from arvo_auth.core.srs_notion_publish_config import ENGINEERING_NOTION_PUBLISH

    return resolve_srs_publish_path(ENGINEERING_NOTION_PUBLISH)


def resolve_srs_publish_path(
    config: SrsNotionPublishTeamConfig,
) -> tuple[Path | None, str | None]:
    root = _project_root()
    raw = config.resolve_publish_input_env()
    if raw:
        p = Path(raw)
        candidate = (
            p.expanduser().resolve() if p.is_absolute() else (root / p).resolve()
        )
    else:
        candidate = config.default_srs_path(root).resolve()

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
    elif not p.is_absolute():
        try:
            candidate.relative_to(root.resolve())
        except ValueError:
            return (
                None,
                f"Relative {config.publish_input_env} must stay under the project root.",
            )

    return candidate, None


def publish_plan_path(config: SrsNotionPublishTeamConfig) -> Path:
    return config.notion_export_dir(_project_root()) / "publish_plan.md"


def publish_execution_log_path(config: SrsNotionPublishTeamConfig) -> Path:
    return config.notion_export_dir(_project_root()) / "publish_execution_log.md"
