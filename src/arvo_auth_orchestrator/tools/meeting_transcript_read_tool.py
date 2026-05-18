"""Read a meeting transcript file from disk (markdown, plain text, srt/vtt, or json)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

_MAX_BYTES = 2_000_000
_ALLOWED_SUFFIXES = frozenset({".md", ".markdown", ".txt", ".vtt", ".srt", ".json"})


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve_transcript_path(raw_override: str = "") -> tuple[Path | None, str | None]:
    """Resolve the transcript file path.

    Precedence: explicit argument (relative to project root or absolute) → env var
    ARVO_MEETING_TRANSCRIPT_FILE. The file must exist, sit under an allowed suffix,
    and remain within the project tree when given a relative path.
    """
    raw = (raw_override or "").strip() or os.getenv("ARVO_MEETING_TRANSCRIPT_FILE", "").strip()
    if not raw:
        return None, (
            "Set ARVO_MEETING_TRANSCRIPT_FILE (absolute or relative to the project root) "
            "or pass `relative_path` with the meeting transcript location."
        )

    root = _project_root()
    p = Path(raw).expanduser()
    candidate = p.resolve() if p.is_absolute() else (root / p).resolve()

    if not candidate.is_file():
        return None, f"Transcript file not found: {candidate}"

    if candidate.suffix.lower() not in _ALLOWED_SUFFIXES:
        return None, (
            f"Refusing transcript suffix {candidate.suffix!r}. Allowed: "
            f"{', '.join(sorted(_ALLOWED_SUFFIXES))}."
        )

    if candidate.stat().st_size > _MAX_BYTES:
        return None, f"Transcript too large (max {_MAX_BYTES} bytes)."

    if not p.is_absolute():
        try:
            candidate.relative_to(root.resolve())
        except ValueError:
            return None, "Relative transcript path must stay under the project root."

    return candidate, None


class MeetingTranscriptReadInput(BaseModel):
    relative_path: str = Field(
        default="",
        description=(
            "Optional path to the transcript (absolute or relative to project root). "
            "If empty, falls back to ARVO_MEETING_TRANSCRIPT_FILE."
        ),
    )


class MeetingTranscriptReadTool(BaseTool):
    name: str = "read_meeting_transcript"
    description: str = (
        "Load a meeting transcript (.md/.txt/.vtt/.srt/.json) from disk. Uses the path "
        "passed in `relative_path` or, when empty, the ARVO_MEETING_TRANSCRIPT_FILE env var."
    )
    args_schema: Type[BaseModel] = MeetingTranscriptReadInput

    def _run(self, relative_path: str = "") -> str:
        path, err = _resolve_transcript_path(relative_path)
        if err:
            return err
        assert path is not None
        return path.read_text(encoding="utf-8", errors="replace")
