from pathlib import Path

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from arvo_auth_orchestrator.llm_defaults import default_llm
from arvo_auth_orchestrator.tools.notion_page_comment_tool import NotionPostPageCommentTool
from arvo_auth_orchestrator.tools.notion_search_tool import NotionSearchPagesTool
from arvo_auth_orchestrator.tools.second_brain_read_tool import SecondBrainReadTool
from arvo_auth_orchestrator.tools.workflow_output_read_tool import WorkflowOutputReadTool


def _load_gap_commenter_identity() -> str:
    root = Path(__file__).resolve().parents[2]
    path = root / "knowledge" / "notion_gap_commenter_identity.md"
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return (
        "(Missing knowledge/notion_gap_commenter_identity.md — restore the Notion gap "
        "commenter prompt file.)"
    )


@CrewBase
class NotionGapCommentCrew:
    """SRS/second-brain gaps and conflicts → Notion search + page comments (REST API)."""

    agents_config = "config/notion_gap_comment_agents.yaml"
    tasks_config = "config/notion_gap_comment_tasks.yaml"

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def notion_gap_commenter(self) -> Agent:
        base = dict(self.agents_config["notion_gap_commenter"])  # type: ignore[arg-type]
        identity = _load_gap_commenter_identity()
        base["backstory"] = f"{base.get('backstory', '')}\n\n{identity}"
        return Agent(
            config=base,
            llm=default_llm(),
            tools=[
                WorkflowOutputReadTool(),
                SecondBrainReadTool(),
                NotionSearchPagesTool(),
                NotionPostPageCommentTool(),
            ],
            verbose=True,
        )

    @task
    def collect_gap_conflict_manifest_task(self) -> Task:
        return Task(
            config=self.tasks_config["collect_gap_conflict_manifest_task"],  # type: ignore[index]
            output_file="outputs/notion_gap_comments/gap_comment_manifest.md",
            markdown=True,
        )

    @task
    def post_notion_clarification_comments_task(self) -> Task:
        return Task(
            config=self.tasks_config["post_notion_clarification_comments_task"],  # type: ignore[index]
            context=[self.collect_gap_conflict_manifest_task()],
            output_file="outputs/notion_gap_comments/gap_comment_execution_log.md",
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
