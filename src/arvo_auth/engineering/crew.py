from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from arvo_auth.core.llm_defaults import default_llm
from arvo_auth.core.tools.second_brain_read_tool import SecondBrainReadTool


@CrewBase
class ArvoAuthOrchestrator:
    """ArvoAuthOrchestrator — SDLC pipeline crew grounded in second-brain knowledge."""

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def planning_lead(self) -> Agent:
        return Agent(
            config=self.agents_config["planning_lead"],  # type: ignore[index]
            llm=default_llm(),
            tools=[SecondBrainReadTool()],
            verbose=True,
        )

    @agent
    def implementation_lead(self) -> Agent:
        return Agent(
            config=self.agents_config["implementation_lead"],  # type: ignore[index]
            llm=default_llm(),
            verbose=True,
        )

    @agent
    def quality_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["quality_analyst"],  # type: ignore[index]
            llm=default_llm(),
            verbose=True,
        )

    @agent
    def maintenance_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config["maintenance_engineer"],  # type: ignore[index]
            llm=default_llm(),
            verbose=True,
        )

    @task
    def discovery_task(self) -> Task:
        return Task(
            config=self.tasks_config["discovery_task"],  # type: ignore[index]
        )

    @task
    def implementation_brief_task(self) -> Task:
        return Task(
            config=self.tasks_config["implementation_brief_task"],  # type: ignore[index]
            context=[self.discovery_task()],
        )

    @task
    def quality_gate_task(self) -> Task:
        return Task(
            config=self.tasks_config["quality_gate_task"],  # type: ignore[index]
            context=[self.discovery_task(), self.implementation_brief_task()],
        )

    @task
    def maintenance_readiness_task(self) -> Task:
        return Task(
            config=self.tasks_config["maintenance_readiness_task"],  # type: ignore[index]
            context=[
                self.discovery_task(),
                self.implementation_brief_task(),
                self.quality_gate_task(),
            ],
            output_file="outputs/engineering/sdlc_pipeline_report.md",
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
