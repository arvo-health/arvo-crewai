"""One-shot runner: invokes NotionPublishViaClaudeTool._run() with plan from disk."""
import os
import sys
from pathlib import Path

# Load .env
env_file = Path(__file__).parents[3] / ".env"
for line in env_file.read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip())

sys.path.insert(0, str(Path(__file__).parents[3] / "src"))

from arvo_auth_orchestrator.tools.notion_publish_claude_tool import NotionPublishViaClaudeTool  # noqa: E402

tool = NotionPublishViaClaudeTool()
result = tool._run("")
print(result)
