from pathlib import Path

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from arvo_auth.core.llm_defaults import default_llm
from arvo_auth.core.tools.notion_publish_claude_tool import NotionPublishViaClaudeTool
from arvo_auth.core.tools.notion_publish_verify_claude_tool import (
    NotionPublishVerifyViaClaudeTool,
)
from arvo_auth.core.tools.srs_publish_read_tool import SrsPublishReadTool


def _load_notion_architect_identity() -> str:
    root = Path(__file__).resolve().parent
    path = root / "knowledge" / "notion_architect_identity.md"
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return (
        "(Missing knowledge/notion_architect_identity.md — restore the Notion Architect "
        "prompt file.)"
    )


@CrewBase
class SrsNotionPublishCrew:
    """Independent crew: SRS.md -> Notion pages (MCP) + completeness audit."""

    agents_config = "config/notion_publish_agents.yaml"
    tasks_config = "config/notion_publish_tasks.yaml"

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def notion_architect(self) -> Agent:
        base = dict(self.agents_config["notion_architect"])  # type: ignore[arg-type]
        identity = _load_notion_architect_identity()
        base["backstory"] = f"{base.get('backstory', '')}\n\n{identity}"
        return Agent(
            config=base,
            llm=default_llm(),
            tools=[
                SrsPublishReadTool(),
                NotionPublishViaClaudeTool(),
                NotionPublishVerifyViaClaudeTool(),
            ],
            verbose=True,
        )

    @task
    def analyze_srs_notion_structure_task(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_srs_notion_structure_task"],  # type: ignore[index]
            output_file="outputs/engineering/notion_export/publish_plan.md",
            markdown=True,
        )

    @task
    def execute_notion_publish_task(self) -> Task:
        return Task(
            config=self.tasks_config["execute_notion_publish_task"],  # type: ignore[index]
            context=[self.analyze_srs_notion_structure_task()],
            output_file="outputs/engineering/notion_export/publish_execution_log.md",
            markdown=True,
        )

    @task
    def verify_notion_publish_completeness_task(self) -> Task:
        return Task(
            config=self.tasks_config["verify_notion_publish_completeness_task"],  # type: ignore[index]
            context=[
                self.analyze_srs_notion_structure_task(),
                self.execute_notion_publish_task(),
            ],
            output_file="outputs/engineering/notion_export/publish_completeness_review.md",
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
