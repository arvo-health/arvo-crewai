"""Crew: decompose SRS into Linear issues and publish them."""

from pathlib import Path

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from arvo_auth.core.llm_defaults import default_llm
from arvo_auth.core.tools.linear_delegate_tool import LinearDelegateTool
from arvo_auth.core.tools.notion_page_tool import NotionPageReadTool
from arvo_auth.core.tools.workflow_output_read_tool import WorkflowOutputReadTool


def _load_identity(filename: str) -> str:
    path = Path(__file__).parent / "knowledge" / filename
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return f"(Missing engineering/knowledge/{filename} — restore the identity file.)"


@CrewBase
class LinearTasksCreationCrew:
    """Two-agent workflow: SRS → issue decomposition → Linear publication."""

    agents_config = "config/linear_tasks_agents.yaml"
    tasks_config = "config/linear_tasks_tasks.yaml"

    agents: list[BaseAgent]
    tasks: list[Task]

    _architect_tools = [
        NotionPageReadTool(),
        WorkflowOutputReadTool(),
    ]

    _publisher_tools = [
        LinearDelegateTool(),
        WorkflowOutputReadTool(),
    ]

    @agent
    def srs_issue_architect(self) -> Agent:
        base = dict(self.agents_config["srs_issue_architect"])  # type: ignore[arg-type]
        identity = _load_identity("srs_issue_architect_identity.md")
        base["backstory"] = f"{base.get('backstory', '')}\n\n{identity}"
        return Agent(
            config=base,
            llm=default_llm(),
            tools=self._architect_tools,
            verbose=True,
        )

    @agent
    def linear_publisher(self) -> Agent:
        base = dict(self.agents_config["linear_publisher"])  # type: ignore[arg-type]
        identity = _load_identity("linear_publisher_identity.md")
        base["backstory"] = f"{base.get('backstory', '')}\n\n{identity}"
        return Agent(
            config=base,
            llm=default_llm(),
            tools=self._publisher_tools,
            verbose=True,
        )

    @task
    def read_srs_task(self) -> Task:
        return Task(
            config=self.tasks_config["read_srs_task"],  # type: ignore[index]
            output_file="outputs/engineering/linear_tasks_creation/01_srs_content.md",
            markdown=True,
        )

    @task
    def decompose_srs_task(self) -> Task:
        return Task(
            config=self.tasks_config["decompose_srs_task"],  # type: ignore[index]
            context=[self.read_srs_task()],
            output_file="outputs/engineering/linear_tasks_creation/02_issues_draft.json",
        )

    @task
    def publish_linear_issues_task(self) -> Task:
        return Task(
            config=self.tasks_config["publish_linear_issues_task"],  # type: ignore[index]
            context=[self.decompose_srs_task()],
            output_file="outputs/engineering/linear_tasks_creation/03_publish_log.md",
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
