"""Crews that turn a meeting transcript into a planned Notion diff (and optional apply).

* `SrsMeetingChangesPlanCrew` — three sequential tasks: (1) meeting manifest from the transcript
  file only, (2) full Notion page/sub-page comment scan via MCP (no local publish/gap artefacts),
  (3) unified diff that merges transcript decisions (`D-*`) and comment suggestions (`C-*`).
  The default CLI entry point `run_srs_meeting_update` stops after this crew finishes (diff
  generated).

* `SrsMeetingChangesApplyCrew` — optional second phase: apply the approved diff on disk via
  Notion MCP and bump Versions. Invoked by `run_srs_meeting_update_apply` after human review
  of `notion_changes_diff.md`.
"""

from pathlib import Path

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from arvo_auth.core.llm_defaults import default_llm
from arvo_auth.core.tools.meeting_transcript_read_tool import (
    MeetingTranscriptReadTool,
)
from arvo_auth.core.tools.meeting_update_artifact_read_tool import (
    MeetingUpdateArtifactReadTool,
)
from arvo_auth.core.tools.notion_apply_srs_changes_claude_tool import (
    NotionApplySrsChangesViaClaudeTool,
)
from arvo_auth.core.tools.notion_collect_page_comments_claude_tool import (
    NotionCollectSrsPageCommentsViaClaudeTool,
)
from arvo_auth.core.tools.notion_update_versions_claude_tool import (
    NotionUpdateVersionsViaClaudeTool,
)
from arvo_auth.core.tools.srs_versions_local_update_tool import (
    SrsVersionsLocalUpdateTool,
)


def _load_change_steward_identity() -> str:
    root = Path(__file__).resolve().parent
    path = root / "knowledge" / "srs_meeting_change_steward_identity.md"
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return (
        "(Missing knowledge/srs_meeting_change_steward_identity.md — restore the SRS "
        "Change Steward prompt file.)"
    )


@CrewBase
class SrsMeetingChangesPlanCrew:
    """Plan SRS changes: transcript manifest + Notion comment scan + unified diff."""

    agents_config = "config/srs_meeting_update_agents.yaml"
    tasks_config = "config/srs_meeting_update_plan_tasks.yaml"

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def srs_change_steward(self) -> Agent:
        base = dict(self.agents_config["srs_change_steward"])  # type: ignore[arg-type]
        identity = _load_change_steward_identity()
        base["backstory"] = f"{base.get('backstory', '')}\n\n{identity}"
        return Agent(
            config=base,
            llm=default_llm(),
            tools=[
                MeetingTranscriptReadTool(),
                NotionCollectSrsPageCommentsViaClaudeTool(),
            ],
            verbose=True,
        )

    @task
    def extract_meeting_decisions_task(self) -> Task:
        return Task(
            config=self.tasks_config["extract_meeting_decisions_task"],  # type: ignore[index]
            output_file="outputs/engineering/srs_meeting_update/srs_changes_manifest.md",
            markdown=True,
        )

    @task
    def collect_notion_comment_suggestions_task(self) -> Task:
        return Task(
            config=self.tasks_config["collect_notion_comment_suggestions_task"],  # type: ignore[index]
            context=[self.extract_meeting_decisions_task()],
            output_file="outputs/engineering/srs_meeting_update/notion_comment_suggestions.md",
            markdown=True,
        )

    @task
    def plan_notion_diff_task(self) -> Task:
        return Task(
            config=self.tasks_config["plan_notion_diff_task"],  # type: ignore[index]
            context=[
                self.extract_meeting_decisions_task(),
                self.collect_notion_comment_suggestions_task(),
            ],
            output_file="outputs/engineering/srs_meeting_update/notion_changes_diff.md",
            markdown=True,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )


@CrewBase
class SrsMeetingChangesApplyCrew:
    """Apply the approved SRS diff to Notion and update Versions section locally + Notion."""

    agents_config = "config/srs_meeting_update_agents.yaml"
    tasks_config = "config/srs_meeting_update_apply_tasks.yaml"

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def srs_change_steward(self) -> Agent:
        base = dict(self.agents_config["srs_change_steward"])  # type: ignore[arg-type]
        identity = _load_change_steward_identity()
        base["backstory"] = f"{base.get('backstory', '')}\n\n{identity}"
        return Agent(
            config=base,
            llm=default_llm(),
            tools=[
                MeetingUpdateArtifactReadTool(),
                NotionApplySrsChangesViaClaudeTool(),
                NotionUpdateVersionsViaClaudeTool(),
                SrsVersionsLocalUpdateTool(),
            ],
            verbose=True,
        )

    @task
    def apply_notion_changes_task(self) -> Task:
        return Task(
            config=self.tasks_config["apply_notion_changes_task"],  # type: ignore[index]
            output_file="outputs/engineering/srs_meeting_update/apply_execution_log.md",
            markdown=True,
        )

    @task
    def update_srs_versions_section_task(self) -> Task:
        return Task(
            config=self.tasks_config["update_srs_versions_section_task"],  # type: ignore[index]
            context=[self.apply_notion_changes_task()],
            output_file="outputs/engineering/srs_meeting_update/versions_update_log.md",
            markdown=True,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
