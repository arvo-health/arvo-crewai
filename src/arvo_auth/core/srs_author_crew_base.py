"""Shared SRS author crew implementation for engineering and copilot teams."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar, TypeVar

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from arvo_auth.core.llm_defaults import default_llm
from arvo_auth.core.srs_crew_config import SrsCrewTeamConfig
from arvo_auth.core.tools.briefing_file_tool import BriefingFileReadTool
from arvo_auth.core.tools.notion_page_tool import NotionPageReadTool
from arvo_auth.core.tools.repo_read_tool import RepoReadTool
from arvo_auth.core.tools.second_brain_read_tool import SecondBrainReadTool
from arvo_auth.core.tools.workflow_output_read_tool import WorkflowOutputReadTool

CrewT = TypeVar("CrewT")


class SrsAuthorCrewMixin:
    """Two-agent workflow: preparation (steps 1–6) then formal SRS (step 7)."""

    team_config: ClassVar[SrsCrewTeamConfig]

    agents: list[BaseAgent]
    tasks: list[Task]

    def _load_identity(self, filename: str) -> str:
        path = self.team_config.knowledge_dir / filename
        if path.is_file():
            return path.read_text(encoding="utf-8")
        return f"(Missing knowledge/{filename} — restore the identity file.)"

    def _workflow_tool(self) -> WorkflowOutputReadTool:
        return WorkflowOutputReadTool(outputs_team=self.team_config.team)

    def _prep_tools(self) -> list:
        return [
            SecondBrainReadTool(),
            NotionPageReadTool(),
            BriefingFileReadTool(),
            RepoReadTool(),
            self._workflow_tool(),
        ]

    def _author_tools(self) -> list:
        return [self._workflow_tool(), BriefingFileReadTool()]

    def _output_path(self, filename: str) -> str:
        return self.team_config.output_path(filename)

    def _build_preparation_lead(self) -> Agent:
        base = dict(self.agents_config["preparation_lead"])  # type: ignore[arg-type,index]
        identity = self._load_identity("context_synthesizer_identity.md")
        base["backstory"] = f"{base.get('backstory', '')}\n\n{identity}"
        return Agent(
            config=base,
            llm=default_llm(),
            tools=self._prep_tools(),
            verbose=True,
        )

    def _build_srs_author(self) -> Agent:
        base = dict(self.agents_config["srs_author"])  # type: ignore[arg-type,index]
        identity = self._load_identity("srs_author_identity.md")
        base["backstory"] = f"{base.get('backstory', '')}\n\n{identity}"
        return Agent(
            config=base,
            llm=default_llm(),
            tools=self._author_tools(),
            verbose=True,
        )

    def _build_ingest_product_overview_task(self) -> Task:
        return Task(
            config=self.tasks_config["ingest_product_overview_task"],  # type: ignore[index]
            output_file=self._output_path("step_01_ingest_memory.md"),
            markdown=True,
        )

    def _build_materialize_overview_task(self) -> Task:
        return Task(
            config=self.tasks_config["materialize_overview_task"],  # type: ignore[index]
            context=[self.ingest_product_overview_task()],
            output_file=self._output_path("overview.md"),
            markdown=True,
        )

    def _build_research_product_details_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_product_details_task"],  # type: ignore[index]
            context=[
                self.ingest_product_overview_task(),
                self.materialize_overview_task(),
            ],
            output_file=self._output_path("product_research_notes.md"),
            markdown=True,
        )

    def _build_materialize_product_task(self) -> Task:
        return Task(
            config=self.tasks_config["materialize_product_task"],  # type: ignore[index]
            context=[
                self.materialize_overview_task(),
                self.research_product_details_task(),
            ],
            output_file=self._output_path("product.md"),
            markdown=True,
        )

    def _build_analyze_codebases_task(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_codebases_task"],  # type: ignore[index]
            context=[
                self.materialize_overview_task(),
                self.research_product_details_task(),
                self.materialize_product_task(),
            ],
            output_file=self._output_path("repo_analysis.md"),
            markdown=True,
        )

    def _build_snapshot_backend_task(self) -> Task:
        return Task(
            config=self.tasks_config["snapshot_backend_task"],  # type: ignore[index]
            context=[
                self.materialize_product_task(),
                self.analyze_codebases_task(),
            ],
            output_file=self._output_path("backend.md"),
            markdown=True,
        )

    def _build_snapshot_frontend_task(self) -> Task:
        return Task(
            config=self.tasks_config["snapshot_frontend_task"],  # type: ignore[index]
            context=[
                self.analyze_codebases_task(),
                self.snapshot_backend_task(),
            ],
            output_file=self._output_path("frontend.md"),
            markdown=True,
        )

    def _build_snapshot_infra_task(self) -> Task:
        return Task(
            config=self.tasks_config["snapshot_infra_task"],  # type: ignore[index]
            context=[
                self.analyze_codebases_task(),
                self.snapshot_backend_task(),
                self.snapshot_frontend_task(),
            ],
            output_file=self._output_path("infra.md"),
            markdown=True,
        )

    def _build_author_srs_task(self) -> Task:
        return Task(
            config=self.tasks_config["author_srs_task"],  # type: ignore[index]
            context=[
                self.ingest_product_overview_task(),
                self.materialize_overview_task(),
                self.research_product_details_task(),
                self.materialize_product_task(),
                self.analyze_codebases_task(),
                self.snapshot_backend_task(),
                self.snapshot_frontend_task(),
                self.snapshot_infra_task(),
            ],
            output_file=self._output_path("SRS.md"),
            markdown=True,
        )

    def _build_crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )


def build_srs_author_crew_class(
    class_name: str,
    srs_team_config: SrsCrewTeamConfig,
    agents_yaml: str,
    tasks_yaml: str,
    package_dir: Path,
) -> type[CrewT]:
    """Create a @CrewBase class with agents/tasks registered on the concrete class.

    CrewAI only discovers @agent/@task methods on the decorated class ``__dict__``,
    not on mixin parents — so each team gets its own generated crew class.

    ``package_dir`` must be the team package (e.g. ``engineering/`` or ``copilot/``)
    so YAML paths resolve next to that team's ``config/`` folder.
    """

    @CrewBase
    class _SrsAuthorCrew(SrsAuthorCrewMixin):
        team_config = srs_team_config
        agents_config = agents_yaml
        tasks_config = tasks_yaml

        @agent
        def preparation_lead(self) -> Agent:
            return self._build_preparation_lead()

        @agent
        def srs_author(self) -> Agent:
            return self._build_srs_author()

        @task
        def ingest_product_overview_task(self) -> Task:
            return self._build_ingest_product_overview_task()

        @task
        def materialize_overview_task(self) -> Task:
            return self._build_materialize_overview_task()

        @task
        def research_product_details_task(self) -> Task:
            return self._build_research_product_details_task()

        @task
        def materialize_product_task(self) -> Task:
            return self._build_materialize_product_task()

        @task
        def analyze_codebases_task(self) -> Task:
            return self._build_analyze_codebases_task()

        @task
        def snapshot_backend_task(self) -> Task:
            return self._build_snapshot_backend_task()

        @task
        def snapshot_frontend_task(self) -> Task:
            return self._build_snapshot_frontend_task()

        @task
        def snapshot_infra_task(self) -> Task:
            return self._build_snapshot_infra_task()

        @task
        def author_srs_task(self) -> Task:
            return self._build_author_srs_task()

        @crew
        def crew(self) -> Crew:
            return self._build_crew()

    _SrsAuthorCrew.base_directory = package_dir
    _SrsAuthorCrew.__name__ = class_name
    _SrsAuthorCrew.__qualname__ = class_name
    return _SrsAuthorCrew
