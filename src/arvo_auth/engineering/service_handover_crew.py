import os
from pathlib import Path

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from arvo_auth.core.llm_defaults import default_llm
from arvo_auth.core.tools.briefing_file_tool import BriefingFileReadTool
from arvo_auth.core.tools.configurable_repo_read_tool import ConfigurableRepoReadTool
from arvo_auth.core.tools.directory_list_tool import DirectoryListTool
from arvo_auth.core.tools.git_log_read_tool import GitLogReadTool


def _load_identity(filename: str) -> str:
    root = Path(__file__).resolve().parent
    path = root / "knowledge" / filename
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return f"(Missing knowledge/{filename} — restore the identity file.)"


def _service_slug(service_path: str) -> str:
    slug = service_path.strip().strip("/").replace("/", "__").replace(" ", "_")
    return slug or "default"


def _output_dir() -> str:
    raw = os.getenv("ARVO_HANDOVER_OUTPUT_DIR", "").strip()
    if raw:
        return raw.rstrip("/")
    slug = _service_slug(os.getenv("ARVO_HANDOVER_SERVICE", "default"))
    return f"outputs/engineering/service_handover/{slug}"


def _handover_filename() -> str:
    slug = _service_slug(os.getenv("ARVO_HANDOVER_SERVICE", "default"))
    return f"{slug}_handover.md"


@CrewBase
class ServiceHandoverCrew:
    """Three-agent sequential crew that produces a service handover document.

    Designed for documenting paused/legacy services in a way that lets the next
    maintainer land cold. Lives in engineering/ as its home, but is generic
    enough to be used by any team (data_science, etc.) via direct import or
    subclassing. Migration to a shared/ home is cheap (see
    docs/crews/crew-service-handover.md).

    Inputs (via kickoff):
      - project_name, repo_name, service_path, current_year
      - status_hint: optional lifecycle hint (active/paused/deprecated/experimental)
      - briefing_markdown: optional extra context
      - backlog_content: verbatim external backlog text (from ARVO_HANDOVER_BACKLOG_FILE)
        or a sentinel string; feeds the archaeologist's pending-plan-items section
      - handover_authoring_rules: text of knowledge/handover_authoring_rules.md
    """

    agents_config = "config/handover_agents.yaml"
    tasks_config = "config/handover_tasks.yaml"

    agents: list[BaseAgent]
    tasks: list[Task]

    _archaeo_tools = [
        ConfigurableRepoReadTool(),
        DirectoryListTool(),
        GitLogReadTool(),
        BriefingFileReadTool(),
    ]
    # Inter-step artefacts (state.md, operations.md) flow via CrewAI task context=
    # wiring, not a re-read tool.
    _chronicler_tools = [
        ConfigurableRepoReadTool(),
        DirectoryListTool(),
        BriefingFileReadTool(),
    ]
    _author_tools = [
        BriefingFileReadTool(),
    ]

    @agent
    def service_archaeologist(self) -> Agent:
        base = dict(self.agents_config["service_archaeologist"])  # type: ignore[arg-type]
        identity = _load_identity("handover_archaeologist_identity.md")
        base["backstory"] = f"{base.get('backstory', '')}\n\n{identity}"
        return Agent(
            config=base,
            llm=default_llm(),
            tools=self._archaeo_tools,
            verbose=True,
        )

    @agent
    def operational_chronicler(self) -> Agent:
        base = dict(self.agents_config["operational_chronicler"])  # type: ignore[arg-type]
        identity = _load_identity("handover_chronicler_identity.md")
        base["backstory"] = f"{base.get('backstory', '')}\n\n{identity}"
        return Agent(
            config=base,
            llm=default_llm(),
            tools=self._chronicler_tools,
            verbose=True,
        )

    @agent
    def handover_author(self) -> Agent:
        base = dict(self.agents_config["handover_author"])  # type: ignore[arg-type]
        identity = _load_identity("handover_author_identity.md")
        base["backstory"] = f"{base.get('backstory', '')}\n\n{identity}"
        return Agent(
            config=base,
            llm=default_llm(),
            tools=self._author_tools,
            verbose=True,
        )

    @task
    def archaeology_task(self) -> Task:
        return Task(
            config=self.tasks_config["archaeology_task"],  # type: ignore[index]
            output_file=f"{_output_dir()}/state.md",
            markdown=True,
        )

    @task
    def operations_task(self) -> Task:
        return Task(
            config=self.tasks_config["operations_task"],  # type: ignore[index]
            context=[self.archaeology_task()],
            output_file=f"{_output_dir()}/operations.md",
            markdown=True,
        )

    @task
    def handover_authoring_task(self) -> Task:
        return Task(
            config=self.tasks_config["handover_authoring_task"],  # type: ignore[index]
            context=[
                self.archaeology_task(),
                self.operations_task(),
            ],
            output_file=f"{_output_dir()}/{_handover_filename()}",
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
