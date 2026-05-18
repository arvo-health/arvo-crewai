"""Deterministically append a new version entry to the local SRS.md (Versions section)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from arvo_auth_orchestrator.tools.srs_publish_read_tool import _resolve_srs_path


# Candidate section titles (case-insensitive). Tolerates optional numbering prefixes
# (`19 `, `19. `, `Annex A `) and optional trailing aliases (`/ Updates`, `e versões`).
_VERSIONS_HEADING_PATTERN = re.compile(
    r"^(#{1,3})\s+"
    r".{0,40}?"
    r"(?:atualizações|updates|histórico de versões|versões|version history)"
    r"(?:[\s/].*)?$",
    re.IGNORECASE,
)


class SrsVersionsLocalUpdateInput(BaseModel):
    version_number: str = Field(
        ...,
        description="New semantic version string to record (e.g. 1.4.0).",
    )
    iso_date: str = Field(
        ...,
        description="ISO-8601 date (YYYY-MM-DD) when the change set was applied.",
    )
    summary_markdown: str = Field(
        ...,
        description=(
            "Short markdown summary of the changes (bullet list preferred). Appended as the "
            "body of the new version entry on the local SRS.md."
        ),
    )


class SrsVersionsLocalUpdateTool(BaseTool):
    name: str = "srs_versions_local_update"
    description: str = (
        "Append a new version entry to the local SRS.md (the same file used by the publish "
        "and meeting-update flows). Creates a Versions/Updates section at the end if missing. "
        "Idempotent for an existing version number: refuses to add a duplicate entry."
    )
    args_schema: Type[BaseModel] = SrsVersionsLocalUpdateInput

    def _run(self, version_number: str, iso_date: str, summary_markdown: str) -> str:
        version = (version_number or "").strip()
        date_str = (iso_date or "").strip()
        summary = (summary_markdown or "").strip()
        if not version or not date_str or not summary:
            return (
                "Missing one of version_number / iso_date / summary_markdown. All three are "
                "required to record a new SRS version entry locally."
            )

        srs_path, err = _resolve_srs_path()
        if err:
            return err
        assert srs_path is not None

        original = srs_path.read_text(encoding="utf-8", errors="replace")
        lines = original.splitlines()

        version_marker = f"## v{version}"
        if any(version_marker in ln for ln in lines):
            return (
                f"Refusing to add duplicate entry: SRS.md already contains '{version_marker}'. "
                "If you meant to amend the entry, edit SRS.md manually."
            )

        section_index: int | None = None
        section_level: int | None = None
        for i, ln in enumerate(lines):
            m = _VERSIONS_HEADING_PATTERN.match(ln)
            if m:
                section_index = i
                section_level = len(m.group(1))
                break

        new_entry = [
            "",
            f"## v{version} — {date_str}",
            "",
            summary,
            "",
        ]

        if section_index is None:
            assert section_level is None
            updated = lines + ["", "# Atualizações / Updates", "", *new_entry[1:]]
            note = "Created new Versions section at end of SRS.md."
        else:
            assert section_level is not None
            insert_at = section_index + 1
            while insert_at < len(lines) and not lines[insert_at].strip():
                insert_at += 1
            updated = lines[:insert_at] + new_entry + lines[insert_at:]
            note = (
                f"Inserted new version entry under existing section at line "
                f"{section_index + 1} (heading level {section_level})."
            )

        srs_path.write_text("\n".join(updated) + "\n", encoding="utf-8")
        return f"OK: {note} New entry: v{version} ({date_str})."
