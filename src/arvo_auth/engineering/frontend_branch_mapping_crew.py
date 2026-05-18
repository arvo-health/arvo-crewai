"""Crew: compare two frontend Git branches and author a product validation mapping."""

from pathlib import Path

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from arvo_auth.core.llm_defaults import default_llm
from arvo_auth.core.tools.github_cli_tool import GitHubCliTool
from arvo_auth.core.tools.repo_read_tool import RepoReadTool
from arvo_auth.core.tools.workflow_output_read_tool import WorkflowOutputReadTool


def _load_frontend_branch_mapper_identity() -> str:
    path = Path(__file__).parent / "knowledge" / "frontend_branch_mapper_identity.md"
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return (
        "(Missing engineering/knowledge/frontend_branch_mapper_identity.md — restore the identity file.)"
    )


@CrewBase
class FrontendBranchMappingCrew:
    """Single-agent workflow: GitHub branch delta → code review → QA mapping artifact."""

    agents_config = "config/frontend_branch_mapping_agents.yaml"
    tasks_config = "config/frontend_branch_mapping_tasks.yaml"

    agents: list[BaseAgent]
    tasks: list[Task]

    _analyst_tools = [
        GitHubCliTool(),
        RepoReadTool(),
        WorkflowOutputReadTool(),
    ]

    @agent
    def frontend_branch_analyst(self) -> Agent:
        base = dict(self.agents_config["frontend_branch_analyst"])  # type: ignore[arg-type]
        identity = _load_frontend_branch_mapper_identity()
        base["backstory"] = f"{base.get('backstory', '')}\n\n{identity}"
        return Agent(
            config=base,
            llm=default_llm(),
            tools=self._analyst_tools,
            verbose=True,
        )

    @task
    def gather_github_branch_delta_task(self) -> Task:
        return Task(
            config=self.tasks_config["gather_github_branch_delta_task"],  # type: ignore[index]
            output_file="outputs/engineering/frontend_branch_mapping/01_github_delta.md",
            markdown=True,
        )

    @task
    def deep_frontend_code_review_task(self) -> Task:
        return Task(
            config=self.tasks_config["deep_frontend_code_review_task"],  # type: ignore[index]
            context=[self.gather_github_branch_delta_task()],
            output_file="outputs/engineering/frontend_branch_mapping/02_code_analysis.md",
            markdown=True,
        )

    @task
    def author_product_mapping_artifact_task(self) -> Task:
        return Task(
            config=self.tasks_config["author_product_mapping_artifact_task"],  # type: ignore[index]
            context=[
                self.gather_github_branch_delta_task(),
                self.deep_frontend_code_review_task(),
            ],
            output_file="outputs/engineering/frontend_branch_mapping/branch_mapping.md",
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
