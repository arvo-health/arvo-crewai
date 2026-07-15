from pathlib import Path

from arvo_auth.core.notion_publish_crew_base import build_srs_notion_publish_crew_class
from arvo_auth.core.srs_notion_publish_config import COPILOT_NOTION_PUBLISH

_PACKAGE_DIR = Path(__file__).resolve().parent

CopilotSrsNotionPublishCrew = build_srs_notion_publish_crew_class(
    class_name="CopilotSrsNotionPublishCrew",
    srs_publish_config=COPILOT_NOTION_PUBLISH,
    agents_yaml="config/notion_publish_agents.yaml",
    tasks_yaml="config/notion_publish_tasks.yaml",
    package_dir=_PACKAGE_DIR,
)
