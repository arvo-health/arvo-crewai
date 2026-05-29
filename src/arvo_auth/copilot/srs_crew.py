from pathlib import Path

from arvo_auth.core.srs_author_crew_base import build_srs_author_crew_class
from arvo_auth.core.srs_crew_config import COPILOT_SRS

_PACKAGE_DIR = Path(__file__).resolve().parent

CopilotSrsAuthorCrew = build_srs_author_crew_class(
    class_name="CopilotSrsAuthorCrew",
    srs_team_config=COPILOT_SRS,
    agents_yaml="config/srs_agents.yaml",
    tasks_yaml="config/srs_tasks.yaml",
    package_dir=_PACKAGE_DIR,
)
