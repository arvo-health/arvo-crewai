"""Crew that applies `notion_changes_diff.md` to Notion only (no Versions sync).

Use `run_srs_notion_diff_apply` from `main` after human review of the diff. For diff + local SRS
Versions + Notion Versions page together, use `run_srs_meeting_update_apply` instead.
"""

from pathlib import Path

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from arvo_auth_orchestrator.llm_defaults import default_llm
from arvo_auth_orchestrator.tools.notion_apply_srs_changes_claude_tool import (
    NotionApplySrsChangesViaClaudeTool,
)


def _load_diff_applier_identity() -> str:
    root = Path(__file__).resolve().parents[2]
    path = root / "knowledge" / "srs_notion_diff_applier_identity.md"
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return (
        "(Missing knowledge/srs_notion_diff_applier_identity.md — restore the Notion Diff "
        "Applier prompt file.)"
    )


@CrewBase
class SrsNotionDiffApplyCrew:
    """Single-task crew: apply the approved Notion diff via MCP."""

    agents_config = "config/srs_notion_diff_apply_agents.yaml"
    tasks_config = "config/srs_notion_diff_apply_tasks.yaml"

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def notion_diff_applier(self) -> Agent:
        base = dict(self.agents_config["notion_diff_applier"])  # type: ignore[arg-type]
        identity = _load_diff_applier_identity()
        base["backstory"] = f"{base.get('backstory', '')}\n\n{identity}"
        return Agent(
            config=base,
            llm=default_llm(),
            tools=[NotionApplySrsChangesViaClaudeTool()],
            verbose=True,
        )

    @task
    def apply_approved_notion_diff_task(self) -> Task:
        return Task(
            config=self.tasks_config["apply_approved_notion_diff_task"],  # type: ignore[index]
            output_file="outputs/srs_meeting_update/diff_apply_execution_log.md",
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
