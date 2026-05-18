from pathlib import Path

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from arvo_auth.core.llm_defaults import default_llm
from arvo_auth.core.tools.briefing_file_tool import BriefingFileReadTool
from arvo_auth.core.tools.notion_page_tool import NotionPageReadTool
from arvo_auth.core.tools.repo_read_tool import RepoReadTool
from arvo_auth.core.tools.second_brain_read_tool import SecondBrainReadTool
from arvo_auth.core.tools.workflow_output_read_tool import WorkflowOutputReadTool


def _load_context_synthesizer_identity() -> str:
    root = Path(__file__).resolve().parent
    path = root / "knowledge" / "context_synthesizer_identity.md"
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return (
        "(Missing knowledge/context_synthesizer_identity.md — restore the Context "
        "Synthesizer prompt file.)"
    )


def _load_srs_author_identity() -> str:
    root = Path(__file__).resolve().parent
    path = root / "knowledge" / "srs_author_identity.md"
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return (
        "(Missing knowledge/srs_author_identity.md — restore the SRS author prompt file.)"
    )


@CrewBase
class SrsAuthorCrew:
    """Two-agent workflow: preparation (steps 1–6) then formal SRS (step 7)."""

    agents_config = "config/srs_agents.yaml"
    tasks_config = "config/srs_tasks.yaml"

    agents: list[BaseAgent]
    tasks: list[Task]

    _prep_tools = [
        SecondBrainReadTool(),
        NotionPageReadTool(),
        BriefingFileReadTool(),
        RepoReadTool(),
        WorkflowOutputReadTool(),
    ]

    @agent
    def preparation_lead(self) -> Agent:
        base = dict(self.agents_config["preparation_lead"])  # type: ignore[arg-type]
        identity = _load_context_synthesizer_identity()
        base["backstory"] = f"{base.get('backstory', '')}\n\n{identity}"
        return Agent(
            config=base,
            llm=default_llm(),
            tools=self._prep_tools,
            verbose=True,
        )

    @agent
    def srs_author(self) -> Agent:
        base = dict(self.agents_config["srs_author"])  # type: ignore[arg-type]
        identity = _load_srs_author_identity()
        base["backstory"] = f"{base.get('backstory', '')}\n\n{identity}"
        return Agent(
            config=base,
            llm=default_llm(),
            tools=[WorkflowOutputReadTool(), BriefingFileReadTool()],
            verbose=True,
        )

    @task
    def ingest_product_overview_task(self) -> Task:
        return Task(
            config=self.tasks_config["ingest_product_overview_task"],  # type: ignore[index]
            output_file="outputs/engineering/srs_workflow/step_01_ingest_memory.md",
            markdown=True,
        )

    @task
    def materialize_overview_task(self) -> Task:
        return Task(
            config=self.tasks_config["materialize_overview_task"],  # type: ignore[index]
            context=[self.ingest_product_overview_task()],
            output_file="outputs/engineering/srs_workflow/overview.md",
            markdown=True,
        )

    @task
    def research_product_details_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_product_details_task"],  # type: ignore[index]
            context=[
                self.ingest_product_overview_task(),
                self.materialize_overview_task(),
            ],
            output_file="outputs/engineering/srs_workflow/product_research_notes.md",
            markdown=True,
        )

    @task
    def materialize_product_task(self) -> Task:
        return Task(
            config=self.tasks_config["materialize_product_task"],  # type: ignore[index]
            context=[
                self.materialize_overview_task(),
                self.research_product_details_task(),
            ],
            output_file="outputs/engineering/srs_workflow/product.md",
            markdown=True,
        )

    @task
    def analyze_codebases_task(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_codebases_task"],  # type: ignore[index]
            context=[
                self.materialize_overview_task(),
                self.research_product_details_task(),
                self.materialize_product_task(),
            ],
            output_file="outputs/engineering/srs_workflow/repo_analysis.md",
            markdown=True,
        )

    @task
    def snapshot_backend_task(self) -> Task:
        return Task(
            config=self.tasks_config["snapshot_backend_task"],  # type: ignore[index]
            context=[
                self.materialize_product_task(),
                self.analyze_codebases_task(),
            ],
            output_file="outputs/engineering/srs_workflow/backend.md",
            markdown=True,
        )

    @task
    def snapshot_frontend_task(self) -> Task:
        return Task(
            config=self.tasks_config["snapshot_frontend_task"],  # type: ignore[index]
            context=[
                self.analyze_codebases_task(),
                self.snapshot_backend_task(),
            ],
            output_file="outputs/engineering/srs_workflow/frontend.md",
            markdown=True,
        )

    @task
    def snapshot_infra_task(self) -> Task:
        return Task(
            config=self.tasks_config["snapshot_infra_task"],  # type: ignore[index]
            context=[
                self.analyze_codebases_task(),
                self.snapshot_backend_task(),
                self.snapshot_frontend_task(),
            ],
            output_file="outputs/engineering/srs_workflow/infra.md",
            markdown=True,
        )

    @task
    def author_srs_task(self) -> Task:
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
            output_file="outputs/engineering/srs_workflow/SRS.md",
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
