# Arvo Auth Orchestrator (CrewAI)

*Portuguese (pt-BR): [README.pt-BR.md](README.pt-BR.md).*

Python package with **CrewAI console entry points** for the Arvo workspace:

| Command | Crew | Purpose |
| --- | --- | --- |
| `crewai run` | `ArvoAuthOrchestrator` | SDLC pipeline (planning → maintenance readiness) |
| `uv run run_srs` | `SrsAuthorCrew` | Product overview → artifacts → **SRS.md** |
| `uv run run_srs_replay` | `SrsAuthorCrew` | **Replay** from a stored task (e.g. regenerate **SRS.md** only; see [crew-srs-author.md](docs/crews/crew-srs-author.md)) |
| `uv run run_notion_publish` | `SrsNotionPublishCrew` | **SRS.md** → Notion **page tree** (Claude Code CLI + MCP) |
| `uv run run_notion_gap_comments` | `NotionGapCommentCrew` | Active gaps/conflicts → **Notion search + page comments** (REST + `NOTION_API_KEY`; see [crew-notion-gap-comments.md](docs/crews/crew-notion-gap-comments.md)) |
| `uv run run_srs_meeting_update` | `SrsMeetingChangesPlanCrew` | Transcript + **full Notion page/sub-page comment scan** → manifest (`D-*`) + comment suggestions (`C-*`) → **`notion_changes_diff.md`** (flow ends here; see [crew-srs-meeting-update.md](docs/crews/crew-srs-meeting-update.md)) |
| `uv run run_srs_meeting_update_apply` | `SrsMeetingChangesApplyCrew` | After manual diff review: apply via MCP + bump Versions on disk and Notion (same doc) |
| `uv run run_srs_notion_diff_apply` | `SrsNotionDiffApplyCrew` | After manual diff review: **apply diff to Notion only** (no Versions step; see [crew-srs-notion-diff-apply.md](docs/crews/crew-srs-notion-diff-apply.md)) |

Per-crew documentation (artifacts, agents, Mermaid flows): [docs/README.md](docs/README.md).

Agent LLM routing is controlled by **`ARVO_LLM_BACKEND`** and **`ANTHROPIC_API_KEY`**:

- **`anthropic`** (default when `ANTHROPIC_API_KEY` is set): CrewAI uses the **Anthropic HTTP API** (`MODEL`, `ANTHROPIC_MAX_TOKENS`).
- **`claude_code`** (default when the API key is **unset**): each agent step runs **`claude -p`** (same binary and flags as Notion delegation). Requires the [Claude Code](https://code.claude.com/docs) CLI on `PATH` or `CLAUDE_CODE_BIN`. Optional: `ARVO_CREWAI_CLAUDE_CODE_TIMEOUT_SEC`, `ARVO_CLAUDE_CODE_CONTEXT_WINDOW`, `ARVO_CLAUDE_CODE_MODEL_LABEL` (label only; the CLI picks the real model).

Set `ARVO_LLM_BACKEND=claude_code` to force the CLI even if `ANTHROPIC_API_KEY` is present.

---

## Prerequisites

- Python `>=3.10,<3.14`
- [uv](https://docs.astral.sh/uv/) (recommended) or `crewai install`
- Either **`ANTHROPIC_API_KEY`** (API mode) or the **`claude`** CLI (CLI mode)

---

## Install

```bash
cd arvo_auth_orchestrator
cp .env.example .env
# Edit .env — API key and/or Claude Code CLI; add Notion vars when using those flows
crewai install
# or: uv sync
```

---

## 1. SDLC crew (`crewai run`)

**Class:** `ArvoAuthOrchestrator` in `crew.py`  
**Config:** `config/agents.yaml`, `config/tasks.yaml`  
**Output:** `outputs/sdlc_pipeline_report.md`

**Inputs (env):** `ARVO_INITIATIVE`, `ARVO_INITIATIVE_BRIEF` (see `main.py`).

Uses **second-brain** reads via `SecondBrainReadTool` when paths appear in the brief. Default second-brain root: sibling `../second-brain` of this project, or `ARVO_SECOND_BRAIN_ROOT`.

---

## 2. SRS workflow (`uv run run_srs`)

**Class:** `SrsAuthorCrew` in `srs_crew.py`  
**Agents:** `preparation_lead` (steps 1–6), `srs_author` (step 7)  
**Artifacts directory:** `outputs/srs_workflow/`

### Steps and files

| Step | Agent | Output file |
| --- | --- | --- |
| 1 | `preparation_lead` | `step_01_ingest_memory.md` |
| 2 | `preparation_lead` | `overview.md` |
| 3 | `preparation_lead` | `product_research_notes.md` |
| 4 | `preparation_lead` | `product.md` |
| 5 | `preparation_lead` | `repo_analysis.md` |
| 6a–c | `preparation_lead` | `backend.md`, `frontend.md`, `infra.md` |
| 7 | `srs_author` | `SRS.md` |

### Prompts and config

- **Context Synthesizer (steps 1–6):** `knowledge/context_synthesizer_identity.md` (injected into `preparation_lead` backstory). Task copy: `config/srs_tasks.yaml`.
- **SRS author (step 7):** `knowledge/srs_author_identity.md` (injected into `srs_author` backstory). Optional org add-ons: `knowledge/srs_authoring_rules.md` or `ARVO_SRS_RULES_FILE`.

### Required / common environment variables

| Variable | Purpose |
| --- | --- |
| `ARVO_SRS_PRODUCT_OVERVIEW` or `ARVO_SRS_OVERVIEW_FILE` | Product input for step 1 |
| `ARVO_SRS_PHASE`, `ARVO_SRS_PROJECT_NAME` | Interpolation in YAML / prompts |
| `ARVO_LLM_BACKEND`, `ANTHROPIC_API_KEY`, `MODEL`, `ANTHROPIC_MAX_TOKENS` | Agent LLM: Anthropic HTTP API or `claude_code` (CLI); see top section |
| `ARVO_CREWAI_CLAUDE_CODE_TIMEOUT_SEC`, `ARVO_CLAUDE_CODE_CONTEXT_WINDOW`, `ARVO_CLAUDE_CODE_MODEL_LABEL` | Optional when using `claude_code` — raise timeout (seconds) for long SRS step 7 / replay; falls back to `NOTION_CLAUDE_DELEGATE_TIMEOUT_SEC`, else default 3600 per LLM call in code |
| `NOTION_VIA_CLAUDE_CODE` | `0`/`false`/`no` = never use CLI; with no key and not disabled → **`claude -p`** delegation (Notion MCP in Claude Code) |
| `ARVO_CLAUDE_CODE_CWD`, `CLAUDE_CODE_BIN`, `CLAUDE_CODE_PERMISSION_MODE`, `NOTION_CLAUDE_DELEGATE_TIMEOUT_SEC`, `CLAUDE_CODE_EXTRA_ARGS` | Tune Claude Code delegation — avoid `dontAsk` for SRS if the CLI tries to use the Write tool (blocks writes); default in code is `acceptEdits` when unset |
| `ARVO_SECOND_BRAIN_ROOT` | Override second-brain root |
| `ARVO_BACKEND_REPO_ROOT`, `ARVO_FRONTEND_REPO_ROOT`, `ARVO_INFRA_REPO_ROOT` | Override repo roots (defaults: sibling `arvo-auth`, `arvo-auth-frontend`; infra defaults to backend tree) |

Run:

```bash
uv run run_srs
```

### Replay step 7 only (`SRS.md`)

After a full successful `run_srs`, CrewAI stores task outputs in SQLite. To re-run **only** the final task (`author_srs_task`), list IDs with `crewai log-tasks-outputs`, then:

Use the **`task_id` field from that command**, not the crew UUID printed in the **Crew Execution Completed** banner (that is the crew run id, not a task id).

```bash
uv run run_srs_replay -- <task_uuid_for_author_srs_task>
# or: ARVO_SRS_REPLAY_TASK_ID=<task_uuid> uv run run_srs_replay
```

Use the **same** SRS-related env vars as for `run_srs`. Do **not** use `uv run replay` for this crew (that entry point targets the SDLC orchestrator). Details: [docs/crews/crew-srs-author.md](docs/crews/crew-srs-author.md).

Step 7 **must** read these seven files via `read_workflow_artifact`: `overview.md`, `product_research_notes.md`, `product.md`, `repo_analysis.md`, `backend.md`, `frontend.md`, `infra.md`.

---

## 3. SRS → Notion publish (`uv run run_notion_publish`)

**Class:** `SrsNotionPublishCrew` in `notion_publish_crew.py`  
**Agent:** `notion_architect`  
**Independence:** Does **not** run the SRS crew; it only reads an existing **SRS.md**.

### Behavior

1. Reads SRS from `ARVO_SRS_PUBLISH_INPUT` or default `outputs/srs_workflow/SRS.md` (`read_srs_for_notion_publish`).
2. Plans a **TOC-driven** tree with **lossless** intent (full markdown per section, no summaries) → `outputs/notion_export/publish_plan.md`.
3. Creates pages via **`notion_publish_srs_via_claude`** → `outputs/notion_export/publish_execution_log.md`.
4. Runs **`notion_verify_srs_publish_completeness_via_claude`** once: compares SRS to live Notion, patches gaps → `outputs/notion_export/publish_completeness_review.md`.

### Environment variables

| Variable | Purpose |
| --- | --- |
| `NOTION_SRS_PARENT_PAGE_ID` | UUID of the **root** Notion page where MCP should attach new pages |
| `NOTION_SRS_PARENT_URL` | Optional full Notion URL of the same root (helps Claude locate the page) |
| `ARVO_SRS_PUBLISH_INPUT` | Optional path to `SRS.md` (absolute, or relative to project root) |
| `NOTION_PUBLISH_CLAUDE_TIMEOUT_SEC` | Subprocess timeout for `claude -p` (default 1800) |
| `NOTION_PUBLISH_VERIFY_CLAUDE_TIMEOUT_SEC` | Subprocess timeout for completeness audit step (default 3600) |

`NOTION_API_KEY` is **not** used by this crew. Publishing is **only** via **`notion_publish_srs_via_claude`** (Claude Code + Notion MCP).

Prompt: `knowledge/notion_architect_identity.md`.

```bash
uv run run_notion_publish
```

**Note:** The subprocess runs `claude` from your PATH with the same MCP config as interactive Claude Code. Use `CLAUDE_CODE_BIN`, `ARVO_CLAUDE_CODE_CWD`, and `CLAUDE_CODE_PERMISSION_MODE` if needed. If the workspace uses a non-default Notion title property, Claude MCP must handle it — there is no REST fallback in this crew.

---

## 4. Notion gap clarification comments (`uv run run_notion_gap_comments`)

**Class:** `NotionGapCommentCrew` in `notion_gap_comment_crew.py`  
**Agent:** `notion_gap_commenter`  
**Independence:** Separate from SRS authoring and from MCP publish; uses **Notion REST** only.

### Behavior

1. Reads `outputs/srs_workflow/gaps_and_open_questions.md` (and optional related workflow files) → `outputs/notion_gap_comments/gap_comment_manifest.md`.
2. For each prioritized gap/conflict, searches Notion and posts an **inline** clarification comment on the chosen page → `outputs/notion_gap_comments/gap_comment_execution_log.md`.

### Environment variables

| Variable | Purpose |
| --- | --- |
| `NOTION_API_KEY` | **Required** — integration must allow **search** and **comment insert** |
| `ARVO_GAP_COMMENT_MAX_ITEMS` | Cap items per run (default `15`) |
| `ARVO_GAP_COMMENT_DRY_RUN` | `1` / `true` / `yes` — skip real comment posts |
| `ARVO_GAP_COMMENT_SOURCES_HINT` | Optional free-text hint for the agent (keywords, priorities) |
| `ARVO_SECOND_BRAIN_ROOT` | Optional — for `open-questions/index.md` and similar reads |

```bash
uv run run_notion_gap_comments
```

Details: [docs/crews/crew-notion-gap-comments.md](docs/crews/crew-notion-gap-comments.md).

---

## 5. SRS meeting update — plan (`uv run run_srs_meeting_update`) and apply (`uv run run_srs_meeting_update_apply`)

**File:** `srs_meeting_update_crew.py`  
**Agents:** `srs_change_steward` on `SrsMeetingChangesPlanCrew` (3 tasks) and `SrsMeetingChangesApplyCrew` (2 tasks)  
**Independence:** The plan crew uses only the meeting transcript and Notion MCP; the apply paths consume `notion_changes_diff.md` from disk (the apply subprocess may still read local SRS/publish files for cross-checks as implemented in the tool).

### Plan command (ends when the diff exists)

1. **Manifest** — transcript file only → `outputs/srs_meeting_update/srs_changes_manifest.md` (`D-*` rows).
2. **Comment sweep** — one `notion_collect_srs_page_comments_via_claude` subprocess walks the Notion workspace root via MCP and **all nested sub-pages** (no local publish logs), listing comment-derived suggestions → `outputs/srs_meeting_update/notion_comment_suggestions.md` (`C-*` plus a page inventory table).
3. **Diff** — merges `D-*` and `C-*` from prior-task context into `outputs/srs_meeting_update/notion_changes_diff.md` (each operation tagged `[D-…]` / `[C-…]`; Notion URLs must come from the comment report inventory).

`main.run_srs_meeting_update()` runs **only** the plan crew, prints paths, and previews the comment report + diff. **No interactive approval loop** and no apply in this command.

### Apply command (optional, after you review the diff file)

- **`uv run run_srs_meeting_update_apply`** — runs `notion_apply_srs_changes_via_claude`, then `srs_versions_local_update` + `notion_update_versions_section_via_claude` (Notion body changes **and** Versions bookkeeping).
- **`uv run run_srs_notion_diff_apply`** — runs **only** `notion_apply_srs_changes_via_claude` (same diff file; **no** local SRS / Notion Versions update). See [crew-srs-notion-diff-apply.md](docs/crews/crew-srs-notion-diff-apply.md).

```bash
uv run run_srs_meeting_update -- /absolute/path/to/transcript.md
# After reviewing outputs/srs_meeting_update/notion_changes_diff.md:
uv run run_srs_notion_diff_apply
# Or, to also record the new version in SRS + Notion:
uv run run_srs_meeting_update_apply
```

### Environment variables

| Variable | Purpose |
| --- | --- |
| `ARVO_MEETING_TRANSCRIPT_FILE` | **Required** for plan — transcript path |
| `NOTION_SRS_PARENT_PAGE_ID` / `NOTION_SRS_PARENT_URL` | **Required** for plan (comment scan) and for apply |
| `ARVO_SRS_PUBLISH_INPUT` | Optional SRS path (default `outputs/srs_workflow/SRS.md`) |
| `NOTION_COMMENT_SCAN_CLAUDE_TIMEOUT_SEC` | Comment sweep subprocess timeout (default `3600`) |
| `ARVO_MEETING_UPDATE_NEXT_VERSION` | Optional semver override in the diff header |
| `NOTION_APPLY_CHANGES_CLAUDE_TIMEOUT_SEC` | Apply subprocess (default `1800`) |
| `NOTION_VERSIONS_UPDATE_CLAUDE_TIMEOUT_SEC` | Versions page subprocess (default `600`) |
| `ARVO_CLAUDE_CODE_CWD`, `CLAUDE_CODE_BIN`, `CLAUDE_CODE_PERMISSION_MODE`, `CLAUDE_CODE_EXTRA_ARGS` | Same Claude Code knobs as the publish crew |

Prompt: `knowledge/srs_meeting_change_steward_identity.md`. Details: [docs/crews/crew-srs-meeting-update.md](docs/crews/crew-srs-meeting-update.md). Diff-only apply: [docs/crews/crew-srs-notion-diff-apply.md](docs/crews/crew-srs-notion-diff-apply.md).

---

## Project layout

```
arvo_auth_orchestrator/
├── knowledge/
│   ├── context_synthesizer_identity.md   # preparation_lead (SRS steps 1–6)
│   ├── srs_author_identity.md          # srs_author (SRS step 7)
│   ├── srs_authoring_rules.md          # optional extras for step 7 task body
│   ├── notion_architect_identity.md    # Notion publish crew
│   ├── notion_gap_commenter_identity.md # Notion gap-comment crew
│   └── srs_meeting_change_steward_identity.md # SRS meeting update crews
├── outputs/
│   ├── srs_workflow/                   # SRS crew artifacts (gitignored *.md)
│   ├── notion_export/                  # publish plan + log (gitignored *.md)
│   ├── notion_gap_comments/            # gap manifest + execution log (gitignored *.md)
│   └── srs_meeting_update/             # manifest + diff + apply + version logs (gitignored *.md)
├── src/arvo_auth_orchestrator/
│   ├── config/
│   │   ├── agents.yaml                 # SDLC crew
│   │   ├── tasks.yaml
│   │   ├── srs_agents.yaml             # SRS crew
│   │   ├── srs_tasks.yaml
│   │   ├── notion_publish_agents.yaml  # Notion publish crew
│   │   ├── notion_publish_tasks.yaml
│   │   ├── notion_gap_comment_agents.yaml
│   │   ├── notion_gap_comment_tasks.yaml
│   │   ├── srs_meeting_update_agents.yaml      # SRS meeting update crews
│   │   ├── srs_meeting_update_plan_tasks.yaml
│   │   └── srs_meeting_update_apply_tasks.yaml
│   ├── tools/
│   │   ├── second_brain_read_tool.py
│   │   ├── notion_page_tool.py         # read Notion (API or Claude CLI delegation)
│   │   ├── notion_claude_delegate.py   # `claude -p` subprocess for Notion MCP
│   │   ├── notion_publish_claude_tool.py # SRS -> Notion via `claude -p` (MCP)
│   │   ├── notion_publish_verify_claude_tool.py # post-publish completeness audit (MCP)
│   │   ├── notion_search_tool.py       # Notion REST search (gap-comment crew)
│   │   ├── notion_page_comment_tool.py # Notion REST page comments
│   │   ├── notion_publish_page_tool.py # optional REST create-page (not used by publish crew)
│   │   ├── notion_api_common.py
│   │   ├── repo_read_tool.py
│   │   ├── workflow_output_read_tool.py
│   │   ├── briefing_file_tool.py
│   │   ├── srs_publish_read_tool.py    # read SRS for publish flow
│   │   ├── meeting_transcript_read_tool.py        # SRS meeting update — load transcript
│   │   ├── meeting_update_artifact_read_tool.py   # SRS meeting update — re-read artefacts
│   │   ├── notion_publish_artifact_read_tool.py   # SRS meeting update — re-read publish plan/log
│   │   ├── notion_collect_page_comments_claude_tool.py # SRS meeting update — comment sweep (MCP)
│   │   ├── notion_apply_srs_changes_claude_tool.py # SRS meeting update — apply diff via MCP
│   │   ├── notion_update_versions_claude_tool.py   # SRS meeting update — Notion Versions page
│   │   └── srs_versions_local_update_tool.py       # SRS meeting update — local SRS Versions append
│   ├── llm_defaults.py                 # API vs Claude Code CLI LLM + HOME bootstrap
│   ├── claude_code_llm.py              # CrewAI BaseLLM -> `claude -p`
│   ├── crew.py                         # ArvoAuthOrchestrator
│   ├── srs_crew.py                     # SrsAuthorCrew
│   ├── notion_publish_crew.py          # SrsNotionPublishCrew
│   ├── notion_gap_comment_crew.py      # NotionGapCommentCrew
│   ├── srs_meeting_update_crew.py      # SrsMeetingChangesPlanCrew + SrsMeetingChangesApplyCrew
│   ├── srs_notion_diff_apply_crew.py   # SrsNotionDiffApplyCrew (diff only, no Versions)
│   └── main.py                         # … run_srs_meeting_update, run_srs_meeting_update_apply, …
├── .env.example
├── pyproject.toml                      # … run_srs_meeting_update, run_srs_meeting_update_apply, …
├── README.md
└── README.pt-BR.md
```

---

## Claude Code (local)

When using **API** mode, keep **`MODEL`** and **`ANTHROPIC_API_KEY`** aligned with your Anthropic project. In **CLI** mode, model selection follows your Claude Code install (`CLAUDE_CODE_EXTRA_ARGS`, etc.). Optional: [CrewAI skills for Claude Code](https://docs.crewai.com/en/guides/coding-tools/build-with-ai) (`/plugin marketplace add crewAIInc/skills`).

---

## Troubleshooting

| Issue | Mitigation |
| --- | --- |
| `onnxruntime` / platform errors on `uv sync` | `[tool.uv] override-dependencies` in `pyproject.toml`; adjust pin if needed. |
| `unable to open database file` (CrewAI SQLite) | Set `ARVO_CREWAI_IN_PROJECT_HOME=1` so state lives under `.crewai_runtime_home/`. |
| Notion 400 on create page | Confirm integration has access to `NOTION_SRS_PARENT_PAGE_ID`; check title property name vs. workspace locale. |
| Notion **403** on `run_notion_gap_comments` | Enable **insert comment** (and search) capabilities for the integration; verify `NOTION_API_KEY`. |

---

## References

- [CrewAI documentation](https://docs.crewai.com/)
- [CrewAI LLMs / Anthropic](https://docs.crewai.com/en/concepts/llms)
- [Notion API — Create a page](https://developers.notion.com/reference/post-page)
