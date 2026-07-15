"""Shared SRS → Linear issue creation crew for engineering and copilot teams."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar, TypeVar

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from arvo_auth.core.linear_tasks_config import LinearTasksTeamConfig
from arvo_auth.core.llm_defaults import default_llm
from arvo_auth.core.tools.linear_delegate_tool import LinearDelegateTool
from arvo_auth.core.tools.notion_page_tool import NotionPageReadTool
from arvo_auth.core.tools.workflow_output_read_tool import WorkflowOutputReadTool

CrewT = TypeVar("CrewT")


class LinearTasksCreationCrewMixin:
    """SRS Notion page → Linear issue tree (Issue Pai + sub-issues per layer)."""

    linear_config: ClassVar[LinearTasksTeamConfig]

    agents: list[BaseAgent]
    tasks: list[Task]

    def _workflow_read_tool(self) -> WorkflowOutputReadTool:
        return WorkflowOutputReadTool(outputs_team=self.linear_config.team)

    def _architect_tools(self) -> list:
        return [
            NotionPageReadTool(),
            self._workflow_read_tool(),
        ]

    def _publisher_tools(self) -> list:
        return [
            LinearDelegateTool(),
            self._workflow_read_tool(),
        ]

    def _load_identity(self, filename: str) -> str:
        path = self.linear_config.knowledge_dir / filename
        if path.is_file():
            return path.read_text(encoding="utf-8")
        return f"(Missing knowledge/{filename} — restore the identity file.)"

    def _build_srs_issue_architect(self) -> Agent:
        base = dict(self.agents_config["srs_issue_architect"])  # type: ignore[arg-type,index]
        identity = self._load_identity("srs_issue_architect_identity.md")
        base["backstory"] = f"{base.get('backstory', '')}\n\n{identity}"
        return Agent(
            config=base,
            llm=default_llm(),
            tools=self._architect_tools(),
            verbose=True,
        )

    def _build_linear_publisher(self) -> Agent:
        base = dict(self.agents_config["linear_publisher"])  # type: ignore[arg-type,index]
        identity = self._load_identity("linear_publisher_identity.md")
        base["backstory"] = f"{base.get('backstory', '')}\n\n{identity}"
        return Agent(
            config=base,
            llm=default_llm(),
            tools=self._publisher_tools(),
            verbose=True,
        )

    def _build_read_srs_task(self) -> Task:
        return Task(
            config=self.tasks_config["read_srs_task"],  # type: ignore[index]
            output_file=self.linear_config.output_path("01_srs_content.md"),
            markdown=True,
        )

    def _build_decompose_srs_task(self) -> Task:
        return Task(
            config=self.tasks_config["decompose_srs_task"],  # type: ignore[index]
            context=[self.read_srs_task()],
            output_file=self.linear_config.output_path("02_issues_draft.json"),
        )

    def _build_publish_linear_issues_task(self) -> Task:
        return Task(
            config=self.tasks_config["publish_linear_issues_task"],  # type: ignore[index]
            context=[self.decompose_srs_task()],
            output_file=self.linear_config.output_path("03_publish_log.md"),
            markdown=True,
        )

    def _build_crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )


def build_linear_tasks_crew_class(
    class_name: str,
    linear_team_config: LinearTasksTeamConfig,
    agents_yaml: str,
    tasks_yaml: str,
    package_dir: Path,
) -> type[CrewT]:
    """Create a @CrewBase class with agents/tasks on the concrete class body."""

    @CrewBase
    class _LinearTasksCreationCrew(LinearTasksCreationCrewMixin):
        linear_config = linear_team_config
        agents_config = agents_yaml
        tasks_config = tasks_yaml

        @agent
        def srs_issue_architect(self) -> Agent:
            return self._build_srs_issue_architect()

        @agent
        def linear_publisher(self) -> Agent:
            return self._build_linear_publisher()

        @task
        def read_srs_task(self) -> Task:
            return self._build_read_srs_task()

        @task
        def decompose_srs_task(self) -> Task:
            return self._build_decompose_srs_task()

        @task
        def publish_linear_issues_task(self) -> Task:
            return self._build_publish_linear_issues_task()

        @crew
        def crew(self) -> Crew:
            return self._build_crew()

    _LinearTasksCreationCrew.base_directory = package_dir
    _LinearTasksCreationCrew.__name__ = class_name
    _LinearTasksCreationCrew.__qualname__ = class_name
    return _LinearTasksCreationCrew
