from pathlib import Path

from arvo_auth.core.linear_tasks_config import ENGINEERING_LINEAR_TASKS
from arvo_auth.core.linear_tasks_crew_base import build_linear_tasks_crew_class

_PACKAGE_DIR = Path(__file__).resolve().parent

LinearTasksCreationCrew = build_linear_tasks_crew_class(
    class_name="LinearTasksCreationCrew",
    linear_team_config=ENGINEERING_LINEAR_TASKS,
    agents_yaml="config/linear_tasks_agents.yaml",
    tasks_yaml="config/linear_tasks_tasks.yaml",
    package_dir=_PACKAGE_DIR,
)
