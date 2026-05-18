# Arvo Auth Orchestrator

Python package with **CrewAI console entry points** for the Arvo workspace. Coordinates multi-crew workflows for software lifecycle management, SRS authoring, and Notion publishing.

*Documentação em Português: [README.pt-BR.md](README.pt-BR.md)*

---

## Prerequisites

- Python `>=3.10,<3.14`
- [uv](https://docs.astral.sh/uv/) (recommended) or `pip`
- Either **`ANTHROPIC_API_KEY`** (API mode) or the **`claude`** CLI in `PATH` (CLI mode)

---

## Install

```bash
cp .env.example .env
# Edit .env — set API key and/or Claude Code CLI vars; add Notion vars for Notion flows
crewai install
# or: uv sync
```

---

## LLM Backend

Agent LLM routing is controlled by `ARVO_LLM_BACKEND` and `ANTHROPIC_API_KEY`:

| Value | Behavior |
| --- | --- |
| `anthropic` (default when key is set) | CrewAI uses Anthropic HTTP API (`MODEL`, `ANTHROPIC_MAX_TOKENS`) |
| `claude_code` (default when key is unset) | Each agent step runs `claude -p` (same binary as Notion delegation) |

Set `ARVO_LLM_BACKEND=claude_code` to force CLI mode even if `ANTHROPIC_API_KEY` is present.

CLI mode options: `CLAUDE_CODE_BIN`, `ARVO_CREWAI_CLAUDE_CODE_TIMEOUT_SEC`, `ARVO_CLAUDE_CODE_CONTEXT_WINDOW`, `ARVO_CLAUDE_CODE_MODEL_LABEL`.

---

## Crews

| Command | Crew | Purpose | Docs |
| --- | --- | --- | --- |
| `crewai run` | `ArvoAuthOrchestrator` | SDLC pipeline: planning → maintenance readiness | [crew-sdlc-pipeline.md](docs/crews/crew-sdlc-pipeline.md) |
| `uv run run_srs` | `SrsAuthorCrew` | Product overview → artifacts → `SRS.md` | [crew-srs-author.md](docs/crews/crew-srs-author.md) |
| `uv run run_srs_replay` | `SrsAuthorCrew` | Replay from a stored task (e.g. regenerate `SRS.md` only) | [crew-srs-author.md](docs/crews/crew-srs-author.md) |
| `uv run run_notion_publish` | `SrsNotionPublishCrew` | `SRS.md` → Notion page tree (Claude Code CLI + MCP) | [crew-srs-notion-publish.md](docs/crews/crew-srs-notion-publish.md) |
| `uv run run_notion_gap_comments` | `NotionGapCommentCrew` | Active gaps/conflicts → Notion search + inline comments | [crew-notion-gap-comments.md](docs/crews/crew-notion-gap-comments.md) |
| `uv run run_srs_meeting_update` | `SrsMeetingChangesPlanCrew` | Transcript + Notion comment scan → `notion_changes_diff.md` | [crew-srs-meeting-update.md](docs/crews/crew-srs-meeting-update.md) |
| `uv run run_srs_meeting_update_apply` | `SrsMeetingChangesApplyCrew` | Apply diff via MCP + bump Versions in SRS and Notion | [crew-srs-meeting-update.md](docs/crews/crew-srs-meeting-update.md) |
| `uv run run_srs_notion_diff_apply` | `SrsNotionDiffApplyCrew` | Apply diff to Notion only (no Versions update) | [crew-srs-notion-diff-apply.md](docs/crews/crew-srs-notion-diff-apply.md) |

Per-crew documentation (agents, artifacts, env vars, Mermaid flows): [docs/README.md](docs/README.md).

---

## Typical Workflows

### SDLC Planning

```bash
crewai run
```

### SRS Authoring → Notion Publish

```bash
uv run run_srs
uv run run_notion_publish
```

### Meeting-Driven SRS Update

```bash
uv run run_srs_meeting_update -- /path/to/transcript.md
# Review outputs/srs_meeting_update/notion_changes_diff.md, then:
uv run run_srs_notion_diff_apply          # Notion only
# or:
uv run run_srs_meeting_update_apply       # Notion + Versions bump
```

---

## Project Layout

```
arvo_auth_orchestrator/
├── knowledge/                            # Agent identity and authoring rules files
├── outputs/                              # Runtime artifacts (gitignored)
│   ├── srs_workflow/
│   ├── notion_export/
│   ├── notion_gap_comments/
│   └── srs_meeting_update/
├── src/arvo_auth_orchestrator/
│   ├── config/                           # agents.yaml + tasks.yaml per crew
│   ├── tools/                            # Custom CrewAI tools (file I/O, Notion REST/MCP)
│   ├── crew.py                           # ArvoAuthOrchestrator (SDLC)
│   ├── srs_crew.py                       # SrsAuthorCrew
│   ├── notion_publish_crew.py            # SrsNotionPublishCrew
│   ├── notion_gap_comment_crew.py        # NotionGapCommentCrew
│   ├── srs_meeting_update_crew.py        # SrsMeetingChangesPlanCrew + ApplyCrew
│   ├── srs_notion_diff_apply_crew.py     # SrsNotionDiffApplyCrew
│   ├── llm_defaults.py                   # LLM backend routing
│   ├── claude_code_llm.py                # CrewAI BaseLLM → `claude -p`
│   └── main.py                           # CLI entry points
├── docs/                                 # Per-crew documentation
│   └── crews/
├── .env.example
└── pyproject.toml
```

---

## Troubleshooting

| Issue | Mitigation |
| --- | --- |
| `onnxruntime` / platform errors on `uv sync` | `[tool.uv] override-dependencies` in `pyproject.toml`; adjust pin if needed. |
| `unable to open database file` (CrewAI SQLite) | Set `ARVO_CREWAI_IN_PROJECT_HOME=1` — state lives under `.crewai_runtime_home/`. |
| Notion 400 on create page | Confirm integration has access to `NOTION_SRS_PARENT_PAGE_ID`; check title property name vs. workspace locale. |
| Notion 403 on `run_notion_gap_comments` | Enable **insert comment** and **search** capabilities for the integration; verify `NOTION_API_KEY`. |

---

## References

- [CrewAI documentation](https://docs.crewai.com/)
- [CrewAI LLMs / Anthropic](https://docs.crewai.com/en/concepts/llms)
- [Notion API — Create a page](https://developers.notion.com/reference/post-page)
