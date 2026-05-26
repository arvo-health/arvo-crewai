"""Read a presentation file (PDF or image) and extract content via Claude Code vision."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from arvo_auth.core.tools.notion_claude_delegate import run_claude_code_print

_SUPPORTED_SUFFIXES = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}
_MAX_BYTES = 50_000_000  # 50 MB — slides export as PDF can be large


def _default_timeout_sec() -> int:
    raw = os.getenv("ARVO_PRESENTATION_READ_TIMEOUT_SEC", "").strip()
    if raw.isdigit():
        return int(raw)
    return 1200


def _build_prompt(file_path: str, focus_hint: str) -> str:
    hint_block = ""
    if focus_hint.strip():
        hint_block = (
            "\n\nFocus hint (use to prioritise sections, but still cover the whole file):\n"
            f"{focus_hint.strip()}\n"
        )

    return (
        "You have multimodal access to local files through the Read tool.\n"
        f"Read the presentation/image file at: {file_path}\n\n"
        "Extract its content as structured markdown:\n"
        "- One '## Slide N — <title>' (or '## Image N') heading per page/image.\n"
        "- Under each heading, write the textual content as bullet points or paragraphs.\n"
        "- For every image, diagram, chart, table or signature embedded in the slide, "
        "  add a '### Visuals' subsection describing in detail what is shown "
        "  (objects, layout, colours, numbers in charts, distinctive features). Be "
        "  literal and specific — downstream agents cannot see the images.\n"
        "- Preserve verbatim any numbers, IDs, dates, names, and Brazilian healthcare "
        "  terms (TISS field numbers, CID, TUSS, etc.).\n"
        "- Do NOT wrap the output in a markdown code fence.\n"
        "- Do NOT summarise — extract everything.\n"
        "- If access fails, return a single paragraph starting with 'ERROR:' and "
        "  state the reason."
        f"{hint_block}"
    )


class PresentationReadInput(BaseModel):
    file_path: str = Field(
        ...,
        description=(
            "Absolute path to a presentation file (.pdf, .png, .jpg, .webp). "
            "Use this when the input is a slide deck export, scanned document, or image."
        ),
    )
    focus_hint: str = Field(
        default="",
        description=(
            "Optional natural-language hint for which sections matter most. "
            "Does not restrict the extraction — only prioritises detail level."
        ),
    )


class PresentationReadTool(BaseTool):
    name: str = "read_presentation"
    description: str = (
        "Read a presentation or image file (PDF, PNG, JPG, WEBP) and extract its "
        "content as structured markdown — including descriptions of images, diagrams, "
        "and signatures. Delegates the visual reading to a `claude -p` subprocess that "
        "has multimodal Read access. Use when the source artefact contains visual "
        "content that plain OCR cannot describe."
    )
    args_schema: Type[BaseModel] = PresentationReadInput

    def _run(self, file_path: str, focus_hint: str = "") -> str:
        raw = file_path.strip()
        if not raw:
            return "ERROR: file_path is empty."

        path = Path(raw).expanduser()
        if not path.is_absolute():
            path = path.resolve()

        if not path.is_file():
            return f"ERROR: file not found at {path}."

        suffix = path.suffix.lower()
        if suffix not in _SUPPORTED_SUFFIXES:
            return (
                f"ERROR: unsupported file type '{suffix}'. "
                f"Supported: {sorted(_SUPPORTED_SUFFIXES)}."
            )

        size = path.stat().st_size
        if size > _MAX_BYTES:
            return (
                f"ERROR: file too large ({size} bytes; max {_MAX_BYTES}). "
                "Split into smaller files or raise the limit."
            )

        prompt = _build_prompt(str(path), focus_hint)
        return run_claude_code_print(prompt, timeout_sec=_default_timeout_sec())
