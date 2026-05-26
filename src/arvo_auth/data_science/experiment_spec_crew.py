from pathlib import Path

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from arvo_auth.core.llm_defaults import default_llm
from arvo_auth.core.tools.briefing_file_tool import BriefingFileReadTool
from arvo_auth.core.tools.configurable_repo_read_tool import ConfigurableRepoReadTool
from arvo_auth.core.tools.presentation_read_tool import PresentationReadTool
from arvo_auth.core.tools.workflow_output_read_tool import WorkflowOutputReadTool


def _load_ds_identity() -> str:
    root = Path(__file__).resolve().parent
    path = root / "knowledge" / "ds_author_identity.md"
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return (
        "(Missing knowledge/ds_author_identity.md — restore the DS author identity file.)"
    )


@CrewBase
class ExperimentSpecCrew:
    """Three-agent sequential crew that produces a data-science experiment_spec.md.

    Inputs (via kickoff):
      - project_name, phase_name, current_year
      - input_pdf_path: path to the discovery artefact (PDF/PNG/etc.)
      - briefing_markdown: extra context appended to the source_analyst prompt
      - experiment_authoring_rules: text of knowledge/experiment_authoring_rules.md
    """

    agents_config = "config/experiment_spec_agents.yaml"
    tasks_config = "config/experiment_spec_tasks.yaml"

    agents: list[BaseAgent]
    tasks: list[Task]

    _analyst_tools = [
        PresentationReadTool(),
        ConfigurableRepoReadTool(),
        BriefingFileReadTool(),
        WorkflowOutputReadTool(),
    ]
    _writer_tools = [
        WorkflowOutputReadTool(),
        BriefingFileReadTool(),
    ]

    @agent
    def source_analyst(self) -> Agent:
        base = dict(self.agents_config["source_analyst"])  # type: ignore[arg-type]
        identity = _load_ds_identity()
        base["backstory"] = f"{base.get('backstory', '')}\n\n{identity}"
        return Agent(
            config=base,
            llm=default_llm(),
            tools=self._analyst_tools,
            verbose=True,
        )

    @agent
    def experiment_designer(self) -> Agent:
        base = dict(self.agents_config["experiment_designer"])  # type: ignore[arg-type]
        identity = _load_ds_identity()
        base["backstory"] = f"{base.get('backstory', '')}\n\n{identity}"
        return Agent(
            config=base,
            llm=default_llm(),
            tools=self._writer_tools,
            verbose=True,
        )

    @agent
    def spec_author(self) -> Agent:
        base = dict(self.agents_config["spec_author"])  # type: ignore[arg-type]
        identity = _load_ds_identity()
        base["backstory"] = f"{base.get('backstory', '')}\n\n{identity}"
        return Agent(
            config=base,
            llm=default_llm(),
            tools=self._writer_tools,
            verbose=True,
        )

    @task
    def map_source_context_task(self) -> Task:
        return Task(
            config=self.tasks_config["map_source_context_task"],  # type: ignore[index]
            output_file="outputs/data_science/experiment_spec/source_context.md",
            markdown=True,
        )

    @task
    def design_experiment_task(self) -> Task:
        return Task(
            config=self.tasks_config["design_experiment_task"],  # type: ignore[index]
            context=[self.map_source_context_task()],
            output_file="outputs/data_science/experiment_spec/experiment_design.md",
            markdown=True,
        )

    @task
    def author_experiment_spec_task(self) -> Task:
        return Task(
            config=self.tasks_config["author_experiment_spec_task"],  # type: ignore[index]
            context=[
                self.map_source_context_task(),
                self.design_experiment_task(),
            ],
            output_file="outputs/data_science/experiment_spec/experiment_spec.md",
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
