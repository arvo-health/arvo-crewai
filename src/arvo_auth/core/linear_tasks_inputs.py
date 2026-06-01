"""Kickoff input builders for SRS → Linear issue creation crews."""

from __future__ import annotations

from datetime import datetime

from arvo_auth.core.linear_tasks_config import LinearTasksTeamConfig
from arvo_auth.core.srs_inputs import _env_value


def build_linear_tasks_kickoff_inputs(config: LinearTasksTeamConfig) -> dict:
    """Build kickoff inputs for a Linear tasks creation crew."""
    page_ref, page_err = config.resolve_srs_notion_page()
    if page_err or not page_ref:
        url_envs = list(config._srs_url_env_names())
        if config.srs_notion_page_id_fallback_env:
            url_envs.append(config.srs_notion_page_id_fallback_env)
        raise ValueError(
            page_err
            or (
                f"Missing SRS Notion page URL. Set {config.srs_notion_page_url_env}"
                + (
                    f" (fallback: {config.srs_notion_page_url_fallback_env})"
                    if config.srs_notion_page_url_fallback_env
                    else ""
                )
                + " to the full Notion URL of the SRS Dashboard page."
            )
        )

    team_key = config.resolve_linear_team_key()
    if not team_key:
        raise ValueError(
            f"Missing Linear team key. Set {config.linear_team_key_env}"
            + (
                f" (or fallback {config.linear_team_key_fallback_env})"
                if config.linear_team_key_fallback_env
                else ""
            )
            + " to the team key in Linear (e.g. COP, NEW, TEA)."
        )

    kickoff = config.kickoff
    project_name = _env_value(kickoff, "PROJECT_NAME") or kickoff.default_project_name
    phase_name = _env_value(kickoff, "PHASE") or "unspecified phase"

    return {
        "project_name": project_name,
        "phase_name": phase_name,
        "srs_notion_page_url": page_ref.url,
        "linear_team_key": team_key,
        "current_year": str(datetime.now().year),
    }


def ensure_linear_tasks_output_dir(config: LinearTasksTeamConfig, project_root) -> None:
    """Create outputs/<team>/linear_tasks_creation/ before kickoff."""
    from pathlib import Path

    root = Path(project_root)
    config.output_dir(root).mkdir(parents=True, exist_ok=True)
