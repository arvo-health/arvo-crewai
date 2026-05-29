#!/usr/bin/env python
import json
import os
import sys
import warnings
from datetime import datetime
from pathlib import Path

from arvo_auth.core.srs_crew_config import COPILOT_SRS, ENGINEERING_SRS, SrsCrewTeamConfig
from arvo_auth.core.srs_inputs import (
    build_notion_publish_kickoff_inputs,
    build_srs_kickoff_inputs,
)
from arvo_auth.core.srs_notion_publish_config import (
    COPILOT_NOTION_PUBLISH,
    ENGINEERING_NOTION_PUBLISH,
    SrsNotionPublishTeamConfig,
)
from arvo_auth.engineering.crew import ArvoAuthOrchestrator


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def _default_inputs() -> dict:
    return {
        "initiative": os.getenv("ARVO_INITIATIVE", "Example initiative"),
        "brief": os.getenv(
            "ARVO_INITIATIVE_BRIEF",
            "Summarize goals and list any second-brain paths to read (e.g. plans/backend/foo/plano.md).",
        ),
        "current_year": str(datetime.now().year),
    }


def run():
    """Run the SDLC pipeline crew."""
    inputs = _default_inputs()
    try:
        ArvoAuthOrchestrator().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}") from e


def _build_srs_inputs() -> dict:
    """Shared kickoff/replay inputs for `SrsAuthorCrew` (engineering team)."""
    return build_srs_kickoff_inputs(ENGINEERING_SRS)


def _build_copilot_srs_inputs() -> dict:
    """Shared kickoff/replay inputs for `CopilotSrsAuthorCrew`."""
    return build_srs_kickoff_inputs(COPILOT_SRS)


def _ensure_srs_output_dir(config: SrsCrewTeamConfig) -> None:
    config.output_dir(_project_root()).mkdir(parents=True, exist_ok=True)


def run_srs():
    """Run the two-agent SRS workflow (artifacts under outputs/engineering/srs_workflow/)."""
    from arvo_auth.engineering.srs_crew import SrsAuthorCrew

    _ensure_srs_output_dir(ENGINEERING_SRS)

    inputs = _build_srs_inputs()
    try:
        SrsAuthorCrew().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the SRS crew: {e}") from e


def _srs_replay_task_id_from_argv() -> str:
    """First non-empty argv token after the script name, ignoring ``--`` (uv / POSIX separator)."""
    for arg in sys.argv[1:]:
        s = arg.strip()
        if not s or s == "--":
            continue
        return s
    return ""


def run_srs_replay():
    """Re-run `SrsAuthorCrew` from a stored task (e.g. pass 7 only) via CrewAI `replay`.

    Requires a prior successful `kickoff` that persisted task outputs (same machine /
    same CrewAI SQLite). Obtain the task UUID with `crewai log-tasks-outputs` and pass
    the row for `author_srs_task` (last task in the SRS pipeline).

    Task id: set `ARVO_SRS_REPLAY_TASK_ID` or pass the UUID on the command line. Tokens
    ``--`` are skipped so both ``uv run run_srs_replay <uuid>`` and
    ``uv run run_srs_replay -- <uuid>`` work.
    """
    from arvo_auth.engineering.srs_crew import SrsAuthorCrew

    task_id = os.getenv("ARVO_SRS_REPLAY_TASK_ID", "").strip()
    if not task_id:
        task_id = _srs_replay_task_id_from_argv()
    if not task_id:
        raise Exception(
            "Missing replay task id. Set ARVO_SRS_REPLAY_TASK_ID or pass the UUID as "
            "the first argument (output of `crewai log-tasks-outputs` for "
            "author_srs_task). Run a full `uv run run_srs` first so outputs are stored."
        )

    root = _project_root()
    _ensure_srs_output_dir(ENGINEERING_SRS)

    inputs = _build_srs_inputs()
    try:
        SrsAuthorCrew().crew().replay(task_id=task_id, inputs=inputs)
    except ValueError as e:
        msg_lower = str(e).lower()
        if "not found" in msg_lower and "task" in msg_lower:
            raise Exception(
                f"An error occurred while replaying the SRS crew: {e}\n\n"
                "The UUID you passed is not a persisted Task id (or nothing is stored). "
                "Do not use the id from the run summary line (Crew Execution Completed / "
                "SrsAuthorCrew id) — that is the crew run id, not a task id. "
                "Run `crewai log-tasks-outputs` in `arvo_auth` and copy "
                "`task_id` from the last row (author_srs_task, step 7). "
                "If the list is empty or from another crew, run `uv run run_srs` again first."
            ) from e
        raise Exception(f"An error occurred while replaying the SRS crew: {e}") from e
    except Exception as e:
        raise Exception(f"An error occurred while replaying the SRS crew: {e}") from e


def run_copilot_srs():
    """Run the SRS workflow for the copilot team (outputs/copilot/srs_workflow/)."""
    from arvo_auth.copilot.srs_crew import CopilotSrsAuthorCrew

    _ensure_srs_output_dir(COPILOT_SRS)

    inputs = _build_copilot_srs_inputs()
    try:
        CopilotSrsAuthorCrew().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(
            f"An error occurred while running the copilot SRS crew: {e}"
        ) from e


def run_copilot_srs_replay():
    """Re-run `CopilotSrsAuthorCrew` from a stored task via CrewAI `replay`.

    Task id: set `ARVO_COPILOT_SRS_REPLAY_TASK_ID` or pass the UUID on the command line.
    """
    from arvo_auth.copilot.srs_crew import CopilotSrsAuthorCrew

    replay_env = COPILOT_SRS.replay_task_id_env or "ARVO_COPILOT_SRS_REPLAY_TASK_ID"
    task_id = os.getenv(replay_env, "").strip()
    if not task_id:
        task_id = _srs_replay_task_id_from_argv()
    if not task_id:
        raise Exception(
            f"Missing replay task id. Set {replay_env} or pass the UUID as "
            "the first argument (output of `crewai log-tasks-outputs` for "
            "author_srs_task). Run a full `uv run run_copilot_srs` first so outputs "
            "are stored."
        )

    _ensure_srs_output_dir(COPILOT_SRS)

    inputs = _build_copilot_srs_inputs()
    try:
        CopilotSrsAuthorCrew().crew().replay(task_id=task_id, inputs=inputs)
    except ValueError as e:
        msg_lower = str(e).lower()
        if "not found" in msg_lower and "task" in msg_lower:
            raise Exception(
                f"An error occurred while replaying the copilot SRS crew: {e}\n\n"
                "The UUID you passed is not a persisted Task id (or nothing is stored). "
                "Do not use the id from the run summary line (Crew Execution Completed / "
                "CopilotSrsAuthorCrew id) — that is the crew run id, not a task id. "
                "Run `crewai log-tasks-outputs` and copy `task_id` from the last row "
                "(author_srs_task, step 7). If the list is empty or from another crew, "
                "run `uv run run_copilot_srs` again first."
            ) from e
        raise Exception(
            f"An error occurred while replaying the copilot SRS crew: {e}"
        ) from e
    except Exception as e:
        raise Exception(
            f"An error occurred while replaying the copilot SRS crew: {e}"
        ) from e


def _ensure_notion_export_dir(config: SrsNotionPublishTeamConfig) -> None:
    config.notion_export_dir(_project_root()).mkdir(parents=True, exist_ok=True)


def run_notion_publish():
    """Publish SRS.md to Notion (engineering team; Claude Code + MCP)."""
    from arvo_auth.engineering.notion_publish_crew import SrsNotionPublishCrew

    _ensure_notion_export_dir(ENGINEERING_NOTION_PUBLISH)

    inputs = build_notion_publish_kickoff_inputs(ENGINEERING_SRS)
    try:
        SrsNotionPublishCrew().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(
            f"An error occurred while running the Notion publish crew: {e}"
        ) from e


def run_copilot_notion_publish():
    """Publish SRS.md to Notion (copilot team; Claude Code + MCP)."""
    from arvo_auth.copilot.notion_publish_crew import CopilotSrsNotionPublishCrew

    _ensure_notion_export_dir(COPILOT_NOTION_PUBLISH)

    inputs = build_notion_publish_kickoff_inputs(COPILOT_SRS)
    try:
        CopilotSrsNotionPublishCrew().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(
            f"An error occurred while running the copilot Notion publish crew: {e}"
        ) from e


def _meeting_update_dir() -> Path:
    return _project_root() / "outputs" / "engineering" / "srs_meeting_update"


def _read_optional_text(path: Path, limit_chars: int = 6000) -> str:
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) <= limit_chars:
        return text
    return text[:limit_chars] + "\n\n[... truncated for terminal display ...]\n"


def _resolve_meeting_transcript_or_raise() -> Path:
    raw = os.getenv("ARVO_MEETING_TRANSCRIPT_FILE", "").strip()
    if not raw and len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            s = arg.strip()
            if not s or s == "--":
                continue
            raw = s
            break
    if not raw:
        raise Exception(
            "Missing meeting transcript. Set ARVO_MEETING_TRANSCRIPT_FILE or pass the path "
            "as the first argument to `uv run run_srs_meeting_update`."
        )
    p = Path(raw).expanduser()
    candidate = p.resolve() if p.is_absolute() else (_project_root() / p).resolve()
    if not candidate.is_file():
        raise Exception(f"Meeting transcript not found at {candidate}.")
    return candidate


def _build_meeting_update_plan_inputs(
    transcript_path: Path,
    revision_iteration: int,
    revision_feedback: str,
    forced_next_version: str,
    auto_approve: bool,
) -> dict:
    return {
        "project_name": os.getenv("ARVO_SRS_PROJECT_NAME", "Arvo authorization"),
        "phase_name": os.getenv("ARVO_SRS_PHASE", "unspecified phase"),
        "current_year": str(datetime.now().year),
        "transcript_path": str(transcript_path),
        "revision_iteration": str(revision_iteration),
        "revision_feedback": revision_feedback or "(none — first iteration)",
        "forced_next_version": forced_next_version or "(none — propose semver from manifest)",
        "auto_approve_mode": "1" if auto_approve else "0",
    }


def _build_meeting_update_apply_inputs(application_date: str) -> dict:
    return {
        "project_name": os.getenv("ARVO_SRS_PROJECT_NAME", "Arvo authorization"),
        "phase_name": os.getenv("ARVO_SRS_PHASE", "unspecified phase"),
        "current_year": str(datetime.now().year),
        "application_date": application_date,
    }


def run_srs_meeting_update():
    """Meeting transcript + Notion comments → manifest, comment report, and diff (ends here).

    Runs `SrsMeetingChangesPlanCrew` only: (1) transcript manifest, (2) full Notion page/sub-page
    comment scan via MCP, (3) unified `notion_changes_diff.md` merging `D-*` and `C-*` sources.

    Required env: ARVO_MEETING_TRANSCRIPT_FILE (or path as first CLI argument),
    NOTION_SRS_PARENT_PAGE_ID or NOTION_SRS_PARENT_URL (for the comment scan subprocess).

    The plan crew uses **only** the transcript file and Notion (MCP) — it does not read
    `publish_execution_log.md`, `SRS.md`, or other crews' outputs.

    To apply the diff and bump Versions after manual review, run `uv run run_srs_meeting_update_apply`.
    """
    from arvo_auth.engineering.srs_meeting_update_crew import SrsMeetingChangesPlanCrew

    transcript_path = _resolve_meeting_transcript_or_raise()
    meeting_dir = _meeting_update_dir()
    meeting_dir.mkdir(parents=True, exist_ok=True)

    forced_next_version = os.getenv("ARVO_MEETING_UPDATE_NEXT_VERSION", "").strip()

    plan_inputs = _build_meeting_update_plan_inputs(
        transcript_path=transcript_path,
        revision_iteration=0,
        revision_feedback="",
        forced_next_version=forced_next_version,
        auto_approve=False,
    )
    try:
        SrsMeetingChangesPlanCrew().crew().kickoff(inputs=plan_inputs)
    except Exception as e:
        raise Exception(
            f"An error occurred while running the SRS meeting plan crew: {e}"
        ) from e

    diff_path = meeting_dir / "notion_changes_diff.md"
    manifest_path = meeting_dir / "srs_changes_manifest.md"
    comments_path = meeting_dir / "notion_comment_suggestions.md"

    if not diff_path.is_file():
        raise Exception(
            f"Plan crew finished but {diff_path} was not produced. Check the agent "
            "verbose log for errors before re-running."
        )

    print("\nSRS meeting update (plan) finished.")
    print(f"  - manifest:           {manifest_path}")
    print(f"  - comment scan:       {comments_path}")
    print(f"  - diff:               {diff_path}")
    print("\n---- Comment scan preview (first 4000 chars) ----")
    print(_read_optional_text(comments_path, limit_chars=4000))
    print("---- Diff preview (first 6000 chars) ----")
    print(_read_optional_text(diff_path))
    print("---- end previews ----\n")
    print(
        "To apply this diff to Notion and update Versions after you review it, run:\n"
        "  uv run run_srs_meeting_update_apply\n"
        "To apply only the Notion operations from the diff (no Versions step), run:\n"
        "  uv run run_srs_notion_diff_apply\n"
    )


def run_srs_meeting_update_apply():
    """Apply `notion_changes_diff.md` to Notion and update SRS Versions (optional second phase).

    Run only after manual review of the diff produced by `uv run run_srs_meeting_update`.
    Requires NOTION_SRS_PARENT_PAGE_ID or NOTION_SRS_PARENT_URL.
    """
    from arvo_auth.engineering.srs_meeting_update_crew import SrsMeetingChangesApplyCrew

    meeting_dir = _meeting_update_dir()
    meeting_dir.mkdir(parents=True, exist_ok=True)

    diff_path = meeting_dir / "notion_changes_diff.md"
    if not diff_path.is_file():
        raise Exception(
            f"No diff at {diff_path}. Run `uv run run_srs_meeting_update` first to generate "
            "the plan artefacts."
        )

    application_date = datetime.now().date().isoformat()
    apply_inputs = _build_meeting_update_apply_inputs(application_date=application_date)
    try:
        SrsMeetingChangesApplyCrew().crew().kickoff(inputs=apply_inputs)
    except Exception as e:
        raise Exception(
            f"An error occurred while running the SRS meeting apply crew: {e}"
        ) from e

    print("\nSRS meeting update (apply) finished.")
    print(f"  - apply log:     {meeting_dir / 'apply_execution_log.md'}")
    print(f"  - versions log:  {meeting_dir / 'versions_update_log.md'}")


def _build_notion_diff_apply_inputs() -> dict:
    return {
        "project_name": os.getenv("ARVO_SRS_PROJECT_NAME", "Arvo authorization"),
        "phase_name": os.getenv("ARVO_SRS_PHASE", "unspecified phase"),
        "current_year": str(datetime.now().year),
    }


def run_srs_notion_diff_apply():
    """Apply only `notion_changes_diff.md` to Notion (no SRS / Notion Versions update).

    Use after manual review of the diff. Requires NOTION_SRS_PARENT_PAGE_ID or
    NOTION_SRS_PARENT_URL. Writes `outputs/engineering/srs_meeting_update/diff_apply_execution_log.md`.

    To also bump the Versions section locally and on Notion, use `uv run run_srs_meeting_update_apply`
    instead.
    """
    from arvo_auth.engineering.srs_notion_diff_apply_crew import SrsNotionDiffApplyCrew

    meeting_dir = _meeting_update_dir()
    meeting_dir.mkdir(parents=True, exist_ok=True)

    diff_path = meeting_dir / "notion_changes_diff.md"
    if not diff_path.is_file():
        raise Exception(
            f"No diff at {diff_path}. Generate a diff first (e.g. `uv run run_srs_meeting_update`)."
        )

    inputs = _build_notion_diff_apply_inputs()
    try:
        SrsNotionDiffApplyCrew().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(
            f"An error occurred while running the Notion diff apply crew: {e}"
        ) from e

    log_path = meeting_dir / "diff_apply_execution_log.md"
    print("\nSRS Notion diff apply finished.")
    print(f"  - diff apply log: {log_path}")


def _frontend_mapping_output_dir() -> Path:
    return _project_root() / "outputs" / "engineering" / "frontend_branch_mapping"


def _default_frontend_github_repo() -> str:
    raw = os.getenv("ARVO_FRONTEND_GITHUB_REPO", "").strip()
    if raw:
        return raw
    frontend_root = os.getenv("ARVO_FRONTEND_REPO_ROOT", "").strip()
    if frontend_root:
        try:
            import subprocess

            from arvo_auth.core.tools.github_cli_common import gh_binary

            binary = gh_binary() or "gh"
            completed = subprocess.run(
                [binary, "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=frontend_root,
                check=False,
            )
            if completed.returncode == 0 and completed.stdout.strip():
                return completed.stdout.strip()
        except OSError:
            pass
    return "arvo-health/arvo-auth-frontend"


def _build_frontend_branch_mapping_inputs() -> dict:
    base = os.getenv("ARVO_BRANCH_BASE", "dev").strip() or "dev"
    head = os.getenv("ARVO_BRANCH_HEAD", "").strip()
    if not head:
        raise Exception(
            "Missing head branch. Set ARVO_BRANCH_HEAD to the feature branch to map "
            "(e.g. TEA-M1)."
        )
    title = os.getenv("ARVO_BRANCH_MAPPING_TITLE", "").strip()
    if not title:
        title = f"{head}-mapping"
    return {
        "project_name": os.getenv("ARVO_SRS_PROJECT_NAME", "Arvo authorization"),
        "github_repo": _default_frontend_github_repo(),
        "base_branch": base,
        "head_branch": head,
        "mapping_title": title,
        "current_year": str(datetime.now().year),
    }


def run_frontend_branch_mapping():
    """Compare two frontend Git branches and write a product validation mapping (M1-mapping style)."""
    from arvo_auth.engineering.frontend_branch_mapping_crew import FrontendBranchMappingCrew

    out_dir = _frontend_mapping_output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)

    inputs = _build_frontend_branch_mapping_inputs()
    try:
        FrontendBranchMappingCrew().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(
            f"An error occurred while running the frontend branch mapping crew: {e}"
        ) from e

    mapping_path = out_dir / "branch_mapping.md"
    print("\nFrontend branch mapping finished.")
    print(f"  - github delta:   {out_dir / '01_github_delta.md'}")
    print(f"  - code analysis:  {out_dir / '02_code_analysis.md'}")
    print(f"  - mapping:        {mapping_path}")
    if mapping_path.is_file():
        preview = mapping_path.read_text(encoding="utf-8", errors="replace")
        if len(preview) > 5000:
            preview = preview[:5000] + "\n\n[... preview truncated ...]\n"
        print("\n---- Mapping preview ----")
        print(preview)
        print("---- end preview ----\n")


def _service_slug_for_handover(service_path: str) -> str:
    slug = service_path.strip().strip("/").replace("/", "__").replace(" ", "_")
    return slug or "default"


def _handover_output_dir() -> Path:
    raw = os.getenv("ARVO_HANDOVER_OUTPUT_DIR", "").strip()
    if raw:
        return Path(raw).expanduser().resolve()
    slug = _service_slug_for_handover(os.getenv("ARVO_HANDOVER_SERVICE", "default"))
    return _project_root() / "outputs" / "engineering" / "service_handover" / slug


def _build_handover_inputs() -> dict:
    """Inputs for `ServiceHandoverCrew` (engineering team)."""
    rules_name = os.getenv(
        "ARVO_HANDOVER_RULES_FILE", "handover_authoring_rules.md"
    ).strip()
    rules_path = (
        Path(__file__).parent / "engineering" / "knowledge" / rules_name
    )
    rules_text = (
        rules_path.read_text(encoding="utf-8")
        if rules_path.is_file()
        else f"(missing rules file at engineering/knowledge/{rules_name})"
    )

    repo_name = os.getenv("ARVO_HANDOVER_REPO", "").strip()
    if not repo_name:
        raise Exception(
            "Missing handover repo. Set ARVO_HANDOVER_REPO to the logical repo "
            "name (e.g. 'intelligence') or pass it as the first CLI argument."
        )

    service_path = os.getenv("ARVO_HANDOVER_SERVICE", "").strip()
    if not service_path:
        raise Exception(
            "Missing handover service path. Set ARVO_HANDOVER_SERVICE to the "
            "sub-path inside the repo (e.g. 'services/doc-quality') or pass it "
            "as the second CLI argument."
        )

    briefing = os.getenv("ARVO_HANDOVER_BRIEFING_MARKDOWN", "").strip()
    if not briefing:
        briefing = "(no extra briefing provided)"

    status_hint = os.getenv("ARVO_HANDOVER_STATUS_HINT", "").strip()
    if not status_hint:
        status_hint = "(none — infer from source signals)"

    backlog_raw = os.getenv("ARVO_HANDOVER_BACKLOG_FILE", "").strip()
    if backlog_raw:
        bp = Path(backlog_raw).expanduser()
        bp = bp.resolve() if bp.is_absolute() else (_project_root() / bp).resolve()
        if bp.is_file():
            text = bp.read_text(encoding="utf-8", errors="replace")
            if len(text) > 80_000:
                text = text[:80_000] + "\n\n[... backlog file truncated at 80KB ...]"
            backlog_content = text
        else:
            backlog_content = f"(ARVO_HANDOVER_BACKLOG_FILE set to {bp} but file not found)"
    else:
        backlog_content = (
            "(no external backlog provided — Section 9 should rely on in-code signals only)"
        )

    return {
        "project_name": os.getenv("ARVO_HANDOVER_PROJECT_NAME", repo_name),
        "repo_name": repo_name,
        "service_path": service_path,
        "status_hint": status_hint,
        "current_year": str(datetime.now().year),
        "briefing_markdown": briefing,
        "backlog_content": backlog_content,
        "handover_authoring_rules": rules_text,
    }


def run_service_handover():
    """Generate a handover document for a single service in a configured repo.

    For paused/legacy services. Reads the service directory, memory-bank,
    git log, deploy configs, and optionally cross-repo consumer references.
    Produces three artefacts under outputs/engineering/service_handover/<slug>/:
      - state.md (factual inventory)
      - operations.md (operational chronicle)
      - <slug>_handover.md (final survival-guide document)

    Required env: ARVO_HANDOVER_REPO, ARVO_HANDOVER_SERVICE
      (also accepted positionally: `uv run run_service_handover -- <repo> <service>`)

    Recommended env: ARVO_HANDOVER_PROJECT_NAME, ARVO_HANDOVER_STATUS_HINT.
    """
    from arvo_auth.engineering.service_handover_crew import ServiceHandoverCrew

    # Allow positional CLI args: repo, then service path.
    positional: list[str] = []
    for arg in sys.argv[1:]:
        s = arg.strip()
        if not s or s == "--":
            continue
        positional.append(s)
    if positional:
        if not os.getenv("ARVO_HANDOVER_REPO", "").strip():
            os.environ["ARVO_HANDOVER_REPO"] = positional[0]
        if len(positional) > 1 and not os.getenv("ARVO_HANDOVER_SERVICE", "").strip():
            os.environ["ARVO_HANDOVER_SERVICE"] = positional[1]

    out_dir = _handover_output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)

    inputs = _build_handover_inputs()
    try:
        ServiceHandoverCrew().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(
            f"An error occurred while running the service handover crew: {e}"
        ) from e

    slug = _service_slug_for_handover(inputs["service_path"])
    handover_path = out_dir / f"{slug}_handover.md"
    print("\nService handover finished.")
    print(f"  - state:     {out_dir / 'state.md'}")
    print(f"  - operations:{out_dir / 'operations.md'}")
    print(f"  - handover:  {handover_path}")


def _build_ds_experiment_spec_inputs() -> dict:
    """Inputs for `ExperimentSpecCrew` (data_science team)."""
    rules_name = os.getenv(
        "ARVO_DS_RULES_FILE", "experiment_authoring_rules.md"
    ).strip()
    rules_path = (
        Path(__file__).parent / "data_science" / "knowledge" / rules_name
    )
    rules_text = (
        rules_path.read_text(encoding="utf-8")
        if rules_path.is_file()
        else f"(missing rules file at data_science/knowledge/{rules_name})"
    )

    input_pdf_raw = os.getenv("ARVO_DS_INPUT_PDF", "").strip()
    if input_pdf_raw:
        p = Path(input_pdf_raw).expanduser()
        input_pdf = p.resolve() if p.is_absolute() else (_project_root() / p).resolve()
        input_pdf_path = str(input_pdf)
    else:
        input_pdf_path = (
            "(Set ARVO_DS_INPUT_PDF to the absolute path of the discovery PDF/PNG.)"
        )

    # Briefing: prefer a file (ARVO_DS_BRIEFING_FILE) over inline markdown. The file form
    # is the home for Phase 0 clarifying-question answers and avoids passing large
    # multi-line content through an inline env var.
    briefing_file = os.getenv("ARVO_DS_BRIEFING_FILE", "").strip()
    if briefing_file:
        bp = Path(briefing_file).expanduser()
        bp = bp.resolve() if bp.is_absolute() else (_project_root() / bp).resolve()
        briefing = (
            bp.read_text(encoding="utf-8", errors="replace")
            if bp.is_file()
            else f"(ARVO_DS_BRIEFING_FILE set to {bp} but file not found)"
        )
    else:
        briefing = os.getenv("ARVO_DS_BRIEFING_MARKDOWN", "").strip()
    if not briefing:
        briefing = "(no extra briefing provided)"

    return {
        "project_name": os.getenv("ARVO_DS_PROJECT_NAME", "data-science experiment"),
        "phase_name": os.getenv("ARVO_DS_PHASE", "poc"),
        "current_year": str(datetime.now().year),
        "input_pdf_path": input_pdf_path,
        "briefing_markdown": briefing,
        "experiment_authoring_rules": rules_text,
    }


def run_ds_experiment_spec():
    """Generate an experiment specification (data_science team).

    Reads a discovery artefact (PDF/PNG) and the configured Arvo repos, then produces
    three artefacts under `outputs/data_science/experiment_spec/`:
      - source_context.md (state of the world)
      - experiment_design.md (research plan)
      - experiment_spec.md (final stakeholder-ready document)

    Required env: ARVO_DS_INPUT_PDF (or first CLI argument).
    Recommended env: ARVO_DS_PROJECT_NAME, ARVO_DS_PHASE,
    ARVO_REPO_INTELLIGENCE, ARVO_REPO_TEA_ANALYZER, ARVO_REPO_ROOTS.
    """
    from arvo_auth.data_science.experiment_spec_crew import ExperimentSpecCrew

    # Allow passing the PDF path as the first CLI argument for ergonomics.
    if not os.getenv("ARVO_DS_INPUT_PDF", "").strip() and len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            s = arg.strip()
            if not s or s == "--":
                continue
            os.environ["ARVO_DS_INPUT_PDF"] = s
            break

    root = _project_root()
    (root / "outputs" / "data_science" / "experiment_spec").mkdir(
        parents=True, exist_ok=True
    )

    inputs = _build_ds_experiment_spec_inputs()
    try:
        ExperimentSpecCrew().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(
            f"An error occurred while running the DS experiment spec crew: {e}"
        ) from e


def run_notion_gap_comments():
    """Post Notion page comments to clarify gaps/conflicts (REST API; requires API key)."""
    from arvo_auth.engineering.notion_gap_comment_crew import NotionGapCommentCrew

    root = _project_root()
    (root / "outputs" / "engineering" / "notion_gap_comments").mkdir(parents=True, exist_ok=True)

    max_raw = os.getenv("ARVO_GAP_COMMENT_MAX_ITEMS", "15").strip()
    max_gap_items = max_raw if max_raw.isdigit() else "15"

    inputs = {
        "project_name": os.getenv("ARVO_SRS_PROJECT_NAME", "Arvo authorization"),
        "phase_name": os.getenv("ARVO_SRS_PHASE", "unspecified phase"),
        "current_year": str(datetime.now().year),
        "max_gap_items": max_gap_items,
        "gap_sources_hint": os.getenv("ARVO_GAP_COMMENT_SOURCES_HINT", "").strip(),
    }
    try:
        NotionGapCommentCrew().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(
            f"An error occurred while running the Notion gap comment crew: {e}"
        ) from e


def train():
    """Train the crew for a given number of iterations."""
    inputs = _default_inputs()
    try:
        ArvoAuthOrchestrator().crew().train(
            n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs
        )
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}") from e


def replay():
    """Replay the crew execution from a specific task."""
    try:
        ArvoAuthOrchestrator().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}") from e


def test():
    """Test the crew execution and return the results."""
    inputs = _default_inputs()
    try:
        ArvoAuthOrchestrator().crew().test(
            n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs
        )
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}") from e


def run_with_trigger():
    """Run the crew with trigger payload (JSON)."""
    if len(sys.argv) < 2:
        raise Exception(
            "No trigger payload provided. Please provide JSON payload as argument."
        )
    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError as exc:
        raise Exception("Invalid JSON payload provided as argument") from exc

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "initiative": trigger_payload.get("initiative", ""),
        "brief": trigger_payload.get("brief", ""),
        "current_year": str(datetime.now().year),
    }
    try:
        return ArvoAuthOrchestrator().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(
            f"An error occurred while running the crew with trigger: {e}"
        ) from e
