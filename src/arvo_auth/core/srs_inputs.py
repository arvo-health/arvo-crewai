"""Kickoff input builders shared by engineering and copilot SRS author crews."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from arvo_auth.core.srs_crew_config import SrsCrewTeamConfig


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _env_value(config: SrsCrewTeamConfig, suffix: str) -> str:
    primary = os.getenv(f"{config.env_prefix}_{suffix}", "").strip()
    if primary:
        return primary
    if config.fallback_env_prefix:
        return os.getenv(f"{config.fallback_env_prefix}_{suffix}", "").strip()
    return ""


def _resolve_overview(config: SrsCrewTeamConfig) -> str:
    overview_file = _env_value(config, "OVERVIEW_FILE")
    if overview_file:
        op = Path(overview_file).expanduser()
        root = _project_root()
        candidate = op.resolve() if op.is_absolute() else (root / op).resolve()
        if candidate.is_file():
            return candidate.read_text(encoding="utf-8")
        return f"(missing overview file: {candidate})"

    product_overview = _env_value(config, "PRODUCT_OVERVIEW")
    if not product_overview:
        product_overview = (
            f"(Set {config.env_prefix}_PRODUCT_OVERVIEW or "
            f"{config.env_prefix}_OVERVIEW_FILE to the product overview for this project/phase.)"
        )
    return product_overview


def _append_briefing(config: SrsCrewTeamConfig, product_overview: str) -> str:
    briefing_file = _env_value(config, "BRIEFING_FILE")
    if briefing_file:
        bp = Path(briefing_file).expanduser()
        root = _project_root()
        candidate = bp.resolve() if bp.is_absolute() else (root / bp).resolve()
        if candidate.is_file():
            text = candidate.read_text(encoding="utf-8", errors="replace")
            product_overview += "\n\n### Additional briefing\n" + text
        else:
            product_overview += (
                f"\n\n### Additional briefing\n"
                f"({config.env_prefix}_BRIEFING_FILE set to {candidate} but file not found)"
            )
        return product_overview

    extra = _env_value(config, "BRIEFING_MARKDOWN")
    if extra:
        product_overview += "\n\n### Additional briefing\n" + extra
    return product_overview


def _append_notion_ids(product_overview: str) -> str:
    notion_ids = os.getenv("NOTION_PAGE_IDS", "").strip()
    if not notion_ids:
        return product_overview
    return product_overview + (
        "\n\n### Notion page IDs\n"
        "Call fetch_notion_page_text once per UUID:\n"
        + "\n".join(p.strip() for p in notion_ids.replace(",", " ").split() if p.strip())
    )


def _load_authoring_rules(config: SrsCrewTeamConfig) -> str:
    rules_name = _env_value(config, "RULES_FILE") or "srs_authoring_rules.md"
    rules_path = config.knowledge_dir / rules_name
    if rules_path.is_file():
        return rules_path.read_text(encoding="utf-8")
    rel = rules_path.relative_to(config.knowledge_dir.parent)
    return f"(missing rules file at {rel})"


def build_srs_kickoff_inputs(config: SrsCrewTeamConfig) -> dict:
    """Build kickoff/replay inputs for an SRS author crew."""
    product_overview = _resolve_overview(config)
    product_overview = _append_briefing(config, product_overview)
    product_overview = _append_notion_ids(product_overview)

    project_name = _env_value(config, "PROJECT_NAME") or config.default_project_name
    phase_name = _env_value(config, "PHASE") or "unspecified phase"

    return {
        "project_name": project_name,
        "phase_name": phase_name,
        "product_overview": product_overview,
        "srs_authoring_rules": _load_authoring_rules(config),
        "current_year": str(datetime.now().year),
    }


def build_notion_publish_kickoff_inputs(config: SrsCrewTeamConfig) -> dict:
    """Kickoff inputs for SRS → Notion publish crews (project/phase only)."""
    project_name = _env_value(config, "PROJECT_NAME") or config.default_project_name
    phase_name = _env_value(config, "PHASE") or "unspecified phase"
    return {
        "project_name": project_name,
        "phase_name": phase_name,
        "current_year": str(datetime.now().year),
    }
