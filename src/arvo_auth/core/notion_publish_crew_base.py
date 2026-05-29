"""Shared SRS → Notion publish crew for engineering and copilot teams."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar, TypeVar

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from arvo_auth.core.llm_defaults import default_llm
from arvo_auth.core.srs_notion_publish_config import SrsNotionPublishTeamConfig
from arvo_auth.core.tools.notion_publish_claude_tool import NotionPublishViaClaudeTool
from arvo_auth.core.tools.notion_publish_verify_claude_tool import (
    NotionPublishVerifyViaClaudeTool,
)
from arvo_auth.core.tools.srs_publish_read_tool import SrsPublishReadTool

CrewT = TypeVar("CrewT")


class SrsNotionPublishCrewMixin:
    """SRS.md → Notion pages (MCP) + completeness audit."""

    publish_config: ClassVar[SrsNotionPublishTeamConfig]

    agents: list[BaseAgent]
    tasks: list[Task]

    def _publish_tools(self) -> list:
        cfg = self.publish_config
        return [
            SrsPublishReadTool(publish_config=cfg),
            NotionPublishViaClaudeTool(publish_config=cfg),
            NotionPublishVerifyViaClaudeTool(publish_config=cfg),
        ]

    def _load_identity(self) -> str:
        path = self.publish_config.knowledge_dir / "notion_architect_identity.md"
        if path.is_file():
            return path.read_text(encoding="utf-8")
        return (
            "(Missing knowledge/notion_architect_identity.md — restore the Notion "
            "Architect prompt file.)"
        )

    def _build_notion_architect(self) -> Agent:
        base = dict(self.agents_config["notion_architect"])  # type: ignore[arg-type,index]
        identity = self._load_identity()
        base["backstory"] = f"{base.get('backstory', '')}\n\n{identity}"
        return Agent(
            config=base,
            llm=default_llm(),
            tools=self._publish_tools(),
            verbose=True,
        )

    def _build_analyze_srs_notion_structure_task(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_srs_notion_structure_task"],  # type: ignore[index]
            output_file=self.publish_config.output_path("publish_plan.md"),
            markdown=True,
        )

    def _build_execute_notion_publish_task(self) -> Task:
        return Task(
            config=self.tasks_config["execute_notion_publish_task"],  # type: ignore[index]
            context=[self.analyze_srs_notion_structure_task()],
            output_file=self.publish_config.output_path("publish_execution_log.md"),
            markdown=True,
        )

    def _build_verify_notion_publish_completeness_task(self) -> Task:
        return Task(
            config=self.tasks_config["verify_notion_publish_completeness_task"],  # type: ignore[index]
            context=[
                self.analyze_srs_notion_structure_task(),
                self.execute_notion_publish_task(),
            ],
            output_file=self.publish_config.output_path(
                "publish_completeness_review.md"
            ),
            markdown=True,
        )

    def _build_crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )


def build_srs_notion_publish_crew_class(
    class_name: str,
    srs_publish_config: SrsNotionPublishTeamConfig,
    agents_yaml: str,
    tasks_yaml: str,
    package_dir: Path,
) -> type[CrewT]:
    """Create a @CrewBase class with agents/tasks on the concrete class body."""

    @CrewBase
    class _SrsNotionPublishCrew(SrsNotionPublishCrewMixin):
        publish_config = srs_publish_config
        agents_config = agents_yaml
        tasks_config = tasks_yaml

        @agent
        def notion_architect(self) -> Agent:
            return self._build_notion_architect()

        @task
        def analyze_srs_notion_structure_task(self) -> Task:
            return self._build_analyze_srs_notion_structure_task()

        @task
        def execute_notion_publish_task(self) -> Task:
            return self._build_execute_notion_publish_task()

        @task
        def verify_notion_publish_completeness_task(self) -> Task:
            return self._build_verify_notion_publish_completeness_task()

        @crew
        def crew(self) -> Crew:
            return self._build_crew()

    _SrsNotionPublishCrew.base_directory = package_dir
    _SrsNotionPublishCrew.__name__ = class_name
    _SrsNotionPublishCrew.__qualname__ = class_name
    return _SrsNotionPublishCrew
