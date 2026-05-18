# Arvo Auth Orchestrator (CrewAI)

Pacote Python com **comandos CrewAI** no workspace Arvo:

| Comando | Crew | Finalidade |
| --- | --- | --- |
| `crewai run` | `ArvoAuthOrchestrator` | Pipeline SDLC (planejamento → prontidão para manutenção) |
| `uv run run_srs` | `SrsAuthorCrew` | Visão de produto → artefatos → **SRS.md** |
| `uv run run_srs_replay` | `SrsAuthorCrew` | **Replay** a partir de uma tarefa gravada (p.ex. só o passo 7; ver [crew-srs-author.md](docs/crews/crew-srs-author.md)) |
| `uv run run_notion_publish` | `SrsNotionPublishCrew` | **SRS.md** → hierarquia no **Notion** (CLI `claude` + MCP) |
| `uv run run_notion_gap_comments` | `NotionGapCommentCrew` | Lacunas/conflitos ativos → **pesquisa + comentários** no Notion (**API REST** + `NOTION_API_KEY`; ver [crew-notion-gap-comments.md](docs/crews/crew-notion-gap-comments.md)) |
| `uv run run_srs_meeting_update` | `SrsMeetingChangesPlanCrew` | Transcrição + **varredura completa de comentários** (páginas e sub-páginas Notion) → manifesto (`D-*`) + sugestões (`C-*`) → **`notion_changes_diff.md`** (fluxo termina aqui; ver [crew-srs-meeting-update.md](docs/crews/crew-srs-meeting-update.md)) |
| `uv run run_srs_meeting_update_apply` | `SrsMeetingChangesApplyCrew` | Após revisão manual do diff: aplicar via MCP + atualizar Versões no disco e no Notion (mesmo doc) |
| `uv run run_srs_notion_diff_apply` | `SrsNotionDiffApplyCrew` | Após revisão manual: **aplicar só o diff no Notion** (sem passo de Versões; ver [crew-srs-notion-diff-apply.md](docs/crews/crew-srs-notion-diff-apply.md)) |

Documentação detalhada por crew (artefactos, agentes, fluxos Mermaid): [docs/README.md](docs/README.md).

O roteamento do LLM dos agentes usa **`ARVO_LLM_BACKEND`** e **`ANTHROPIC_API_KEY`**:

- **`anthropic`** (padrão quando `ANTHROPIC_API_KEY` está definida): CrewAI chama a **API HTTP Anthropic** (`MODEL`, `ANTHROPIC_MAX_TOKENS`).
- **`claude_code`** (padrão quando a chave **não** está definida): cada passo do agente executa **`claude -p`** (mesmo binário que a delegação Notion). Exige o CLI [Claude Code](https://code.claude.com/docs) no `PATH` ou `CLAUDE_CODE_BIN`. Opcional: `ARVO_CREWAI_CLAUDE_CODE_TIMEOUT_SEC`, `ARVO_CLAUDE_CODE_CONTEXT_WINDOW`, `ARVO_CLAUDE_CODE_MODEL_LABEL` (só rótulo; o modelo real vem do Claude Code).

Defina `ARVO_LLM_BACKEND=claude_code` para forçar o CLI mesmo com `ANTHROPIC_API_KEY` presente.

*Versão em inglês: [README.md](README.md).*

---

## Pré-requisitos

- Python `>=3.10,<3.14`
- [uv](https://docs.astral.sh/uv/) (recomendado) ou `crewai install`
- Ou **`ANTHROPIC_API_KEY`** (modo API) ou o CLI **`claude`** (modo CLI)

---

## Instalação

```bash
cd arvo_auth_orchestrator
cp .env.example .env
# Edite o .env — chave API e/ou Claude Code CLI; variáveis Notion quando usar esses fluxos
crewai install
# ou: uv sync
```

---

## 1. Crew SDLC (`crewai run`)

**Classe:** `ArvoAuthOrchestrator` em `crew.py`  
**Configuração:** `config/agents.yaml`, `config/tasks.yaml`  
**Saída:** `outputs/sdlc_pipeline_report.md`

**Entradas (variáveis de ambiente):** `ARVO_INITIATIVE`, `ARVO_INITIATIVE_BRIEF` (ver `main.py`).

Usa leituras do **second-brain** via `SecondBrainReadTool` quando o briefing citar caminhos. Raiz padrão do second-brain: pasta irmã `../second-brain` deste projeto, ou `ARVO_SECOND_BRAIN_ROOT`.

---

## 2. Fluxo SRS (`uv run run_srs`)

**Classe:** `SrsAuthorCrew` em `srs_crew.py`  
**Agentes:** `preparation_lead` (passos 1–6), `srs_author` (passo 7)  
**Diretório de artefatos:** `outputs/srs_workflow/`

### Passos e arquivos

| Passo | Agente | Arquivo gerado |
| --- | --- | --- |
| 1 | `preparation_lead` | `step_01_ingest_memory.md` |
| 2 | `preparation_lead` | `overview.md` |
| 3 | `preparation_lead` | `product_research_notes.md` |
| 4 | `preparation_lead` | `product.md` |
| 5 | `preparation_lead` | `repo_analysis.md` |
| 6a–c | `preparation_lead` | `backend.md`, `frontend.md`, `infra.md` |
| 7 | `srs_author` | `SRS.md` |

### Prompts e configuração

- **Context Synthesizer (passos 1–6):** `knowledge/context_synthesizer_identity.md` (injetado no `backstory` do `preparation_lead`). Texto das tarefas: `config/srs_tasks.yaml`.
- **Autor do SRS (passo 7):** `knowledge/srs_author_identity.md` (injetado no `backstory` do `srs_author`). Complementos opcionais da organização: `knowledge/srs_authoring_rules.md` ou `ARVO_SRS_RULES_FILE`.

### Variáveis de ambiente usuais / necessárias

| Variável | Finalidade |
| --- | --- |
| `ARVO_SRS_PRODUCT_OVERVIEW` ou `ARVO_SRS_OVERVIEW_FILE` | Entrada de produto no passo 1 |
| `ARVO_SRS_PHASE`, `ARVO_SRS_PROJECT_NAME` | Interpolação no YAML / prompts |
| `ARVO_LLM_BACKEND`, `ANTHROPIC_API_KEY`, `MODEL`, `ANTHROPIC_MAX_TOKENS` | LLM dos agentes: API Anthropic ou `claude_code` (CLI); ver secção no topo |
| `ARVO_CREWAI_CLAUDE_CODE_TIMEOUT_SEC`, `ARVO_CLAUDE_CODE_CONTEXT_WINDOW`, `ARVO_CLAUDE_CODE_MODEL_LABEL` | Opcional no modo `claude_code` — aumenta o timeout (segundos) para SRS longo no passo 7 ou replay; se vazio, usa `NOTION_CLAUDE_DELEGATE_TIMEOUT_SEC`, senão default 3600 por chamada LLM no código |
| `NOTION_VIA_CLAUDE_CODE` | `0`/`false`/`no` = não usar o CLI; sem chave e sem desativar = **delegação ao `claude -p`** (MCP Notion no Claude Code) |
| `ARVO_CLAUDE_CODE_CWD`, `CLAUDE_CODE_BIN`, `CLAUDE_CODE_PERMISSION_MODE`, `NOTION_CLAUDE_DELEGATE_TIMEOUT_SEC`, `CLAUDE_CODE_EXTRA_ARGS` | Ajustes da delegação ao Claude Code — evita `dontAsk` no SRS se o CLI usar a ferramenta Write (bloqueia escrita); o default no código é `acceptEdits` se a variável não estiver definida |
| `ARVO_SECOND_BRAIN_ROOT` | Sobrescrever raiz do second-brain |
| `ARVO_BACKEND_REPO_ROOT`, `ARVO_FRONTEND_REPO_ROOT`, `ARVO_INFRA_REPO_ROOT` | Sobrescrever raízes dos repositórios (padrão: irmãos `arvo-auth`, `arvo-auth-frontend`; infra usa a árvore do backend por padrão) |

Execução:

```bash
uv run run_srs
```

### Replay só do passo 7 (`SRS.md`)

Depois de um `run_srs` completo com sucesso, o CrewAI grava saídas das tarefas em SQLite. Para **reexecutar só** a tarefa final (`author_srs_task`), lista os IDs com `crewai log-tasks-outputs` e:

Usa o campo **`task_id`** desse comando, **não** o UUID do banner **Crew Execution Completed** (esse é o id do crew, não de uma tarefa).

```bash
uv run run_srs_replay -- <task_uuid_da_author_srs_task>
# ou: ARVO_SRS_REPLAY_TASK_ID=<task_uuid> uv run run_srs_replay
```

Usa as **mesmas** variáveis de ambiente do fluxo SRS que em `run_srs`. **Não** uses `uv run replay` para este crew (esse comando é o crew SDLC). Detalhes: [docs/crews/crew-srs-author.md](docs/crews/crew-srs-author.md).

No passo 7 é **obrigatório** ler estes sete arquivos com `read_workflow_artifact`: `overview.md`, `product_research_notes.md`, `product.md`, `repo_analysis.md`, `backend.md`, `frontend.md`, `infra.md`.

---

## 3. Publicação SRS → Notion (`uv run run_notion_publish`)

**Classe:** `SrsNotionPublishCrew` em `notion_publish_crew.py`  
**Agente:** `notion_architect`  
**Independência:** **Não** executa o crew de SRS; apenas lê um **SRS.md** já existente.

### Comportamento

1. Lê o SRS de `ARVO_SRS_PUBLISH_INPUT` ou padrão `outputs/srs_workflow/SRS.md` (`read_srs_for_notion_publish`).
2. Planeja uma árvore **guiada pelo sumário (TOC)** com intenção **sem perda** (corpo completo por secção) → `outputs/notion_export/publish_plan.md`.
3. Cria a hierarquia no Notion via **`notion_publish_srs_via_claude`** (CLI `claude` + MCP) → `outputs/notion_export/publish_execution_log.md`.
4. Corre **`notion_verify_srs_publish_completeness_via_claude`** uma vez: compara o SRS às páginas, corrige lacunas via MCP → `outputs/notion_export/publish_completeness_review.md`.

### Variáveis de ambiente

| Variável | Finalidade |
| --- | --- |
| `NOTION_SRS_PARENT_PAGE_ID` | UUID da página Notion **raiz** onde o MCP deve criar as subpáginas |
| `NOTION_SRS_PARENT_URL` | URL completa opcional da mesma raiz (ajuda o Claude a localizar a página) |
| `ARVO_SRS_PUBLISH_INPUT` | Caminho opcional para o `SRS.md` (absoluto ou relativo à raiz do projeto) |
| `NOTION_PUBLISH_CLAUDE_TIMEOUT_SEC` | Timeout do subprocess `claude -p` do passo 3 (padrão 1800) |
| `NOTION_PUBLISH_VERIFY_CLAUDE_TIMEOUT_SEC` | Timeout do subprocess do passo 4 — auditoria (padrão 3600) |

Este crew **não** usa `NOTION_API_KEY` para criar páginas. Os passos 3 e 4 usam **`notion_publish_srs_via_claude`** e **`notion_verify_srs_publish_completeness_via_claude`** (Claude Code + MCP Notion).

Prompt: `knowledge/notion_architect_identity.md`.

```bash
uv run run_notion_publish
```

**Observação:** o subprocess executa `claude` do PATH com a mesma configuração MCP do Claude Code interativo. Use `CLAUDE_CODE_BIN`, `ARVO_CLAUDE_CODE_CWD` e `CLAUDE_CODE_PERMISSION_MODE` se precisar. Não há fallback REST neste crew.

---

## 4. Comentários Notion para lacunas (`uv run run_notion_gap_comments`)

**Classe:** `NotionGapCommentCrew` em `notion_gap_comment_crew.py`  
**Agente:** `notion_gap_commenter`  
**Independência:** Usa só **API REST Notion** (não é o fluxo MCP de publicação do SRS).

### Comportamento

1. Lê `outputs/srs_workflow/gaps_and_open_questions.md` (e ficheiros relacionados opcionais) → `outputs/notion_gap_comments/gap_comment_manifest.md`.
2. Pesquisa páginas no Notion e publica **comentários** com perguntas de esclarecimento → `outputs/notion_gap_comments/gap_comment_execution_log.md`.

### Variáveis de ambiente

| Variável | Finalidade |
| --- | --- |
| `NOTION_API_KEY` | **Obrigatório** — integração com pesquisa e **inserção de comentários** |
| `ARVO_GAP_COMMENT_MAX_ITEMS` | Limite de itens por corrida (padrão `15`) |
| `ARVO_GAP_COMMENT_DRY_RUN` | `1` / `true` / `yes` — não publica comentários reais |
| `ARVO_GAP_COMMENT_SOURCES_HINT` | Texto livre com prioridades ou palavras-chave extra |
| `ARVO_SECOND_BRAIN_ROOT` | Opcional — para ler `open-questions/index.md`, etc. |

```bash
uv run run_notion_gap_comments
```

Detalhes: [docs/crews/crew-notion-gap-comments.md](docs/crews/crew-notion-gap-comments.md).

---

## 5. Atualização SRS por reunião — plano (`uv run run_srs_meeting_update`) e aplicar (`uv run run_srs_meeting_update_apply`)

**Ficheiro:** `srs_meeting_update_crew.py`  
**Agente:** `srs_change_steward` no crew de plano (3 tarefas) e no crew de aplicar (2 tarefas)  
**Independência:** O crew de plano usa só a transcrição e o Notion via MCP; os comandos de aplicar consomem `notion_changes_diff.md` em disco (o subprocesso de apply pode ainda ler SRS ou artefactos de publicação para verificações, conforme a ferramenta).

### Comando de plano (termina com o diff)

1. **Manifesto** — só o ficheiro de transcrição → `outputs/srs_meeting_update/srs_changes_manifest.md` (`D-*`).
2. **Varredura de comentários** — um subprocesso `notion_collect_srs_page_comments_via_claude` percorre a raiz Notion via MCP e **todas as sub-páginas** (sem ler `publish_execution_log.md` nem outros artefactos locais de outros crews) → `outputs/srs_meeting_update/notion_comment_suggestions.md` (`C-*` + inventário de páginas).
3. **Diff** — funde `D-*` e `C-*` (contexto das tarefas anteriores) em `outputs/srs_meeting_update/notion_changes_diff.md` (cada operação com `[D-…]` / `[C-…]`; URLs Notion apenas a partir do inventário do passo 2).

`main.run_srs_meeting_update()` executa **só** o crew de plano, imprime caminhos e pré-visualiza comentários + diff. **Sem** loop interactivo de aprovação e **sem** aplicar neste comando.

### Comando de aplicar (opcional, após rever o ficheiro do diff)

- **`uv run run_srs_meeting_update_apply`** — `notion_apply_srs_changes_via_claude`, depois `srs_versions_local_update` + `notion_update_versions_section_via_claude` (alterações no Notion **e** registo de Versões).
- **`uv run run_srs_notion_diff_apply`** — **apenas** `notion_apply_srs_changes_via_claude` (mesmo ficheiro de diff; **sem** Versões no `SRS.md` local nem na página Notion). Ver [crew-srs-notion-diff-apply.md](docs/crews/crew-srs-notion-diff-apply.md).

```bash
uv run run_srs_meeting_update -- /caminho/absoluto/transcript.md
# Depois de rever outputs/srs_meeting_update/notion_changes_diff.md:
uv run run_srs_notion_diff_apply
# Ou, para também gravar a nova versão no SRS + Notion:
uv run run_srs_meeting_update_apply
```

### Variáveis de ambiente

| Variável | Finalidade |
| --- | --- |
| `ARVO_MEETING_TRANSCRIPT_FILE` | **Obrigatório** no plano — caminho da transcrição |
| `NOTION_SRS_PARENT_PAGE_ID` / `NOTION_SRS_PARENT_URL` | **Obrigatório** (varredura + aplicar) |
| `ARVO_SRS_PUBLISH_INPUT` | Caminho opcional do `SRS.md` (default `outputs/srs_workflow/SRS.md`) |
| `NOTION_COMMENT_SCAN_CLAUDE_TIMEOUT_SEC` | Timeout da varredura de comentários (default `3600`) |
| `ARVO_MEETING_UPDATE_NEXT_VERSION` | Override semver opcional no cabeçalho do diff |
| `NOTION_APPLY_CHANGES_CLAUDE_TIMEOUT_SEC` | Apply (default `1800`) |
| `NOTION_VERSIONS_UPDATE_CLAUDE_TIMEOUT_SEC` | Página Versões (default `600`) |
| `ARVO_CLAUDE_CODE_CWD`, `CLAUDE_CODE_BIN`, `CLAUDE_CODE_PERMISSION_MODE`, `CLAUDE_CODE_EXTRA_ARGS` | Mesmos ajustes Claude Code dos outros crews |

Prompt: `knowledge/srs_meeting_change_steward_identity.md`. Detalhes: [docs/crews/crew-srs-meeting-update.md](docs/crews/crew-srs-meeting-update.md). Aplicar só o diff: [docs/crews/crew-srs-notion-diff-apply.md](docs/crews/crew-srs-notion-diff-apply.md).

---

## Layout do projeto

```
arvo_auth_orchestrator/
├── knowledge/
│   ├── context_synthesizer_identity.md   # preparation_lead (SRS passos 1–6)
│   ├── srs_author_identity.md          # srs_author (SRS passo 7)
│   ├── srs_authoring_rules.md          # extras opcionais no corpo da tarefa do passo 7
│   ├── notion_architect_identity.md    # crew de publicação no Notion
│   ├── notion_gap_commenter_identity.md # crew de comentários (lacunas)
│   └── srs_meeting_change_steward_identity.md # crews de atualização do SRS por reunião
├── outputs/
│   ├── srs_workflow/                   # artefatos do crew SRS (*.md no .gitignore)
│   ├── notion_export/                  # plano + log de publicação (*.md no .gitignore)
│   ├── notion_gap_comments/            # manifesto + log de comentários (*.md no .gitignore)
│   └── srs_meeting_update/             # manifesto + diff + logs (*.md no .gitignore)
├── src/arvo_auth_orchestrator/
│   ├── config/
│   │   ├── agents.yaml                 # crew SDLC
│   │   ├── tasks.yaml
│   │   ├── srs_agents.yaml             # crew SRS
│   │   ├── srs_tasks.yaml
│   │   ├── notion_publish_agents.yaml  # crew publicação Notion
│   │   ├── notion_publish_tasks.yaml
│   │   ├── notion_gap_comment_agents.yaml
│   │   ├── notion_gap_comment_tasks.yaml
│   │   ├── srs_meeting_update_agents.yaml          # crews de atualização por reunião
│   │   ├── srs_meeting_update_plan_tasks.yaml
│   │   └── srs_meeting_update_apply_tasks.yaml
│   ├── tools/
│   │   ├── second_brain_read_tool.py
│   │   ├── notion_page_tool.py         # leitura de páginas Notion (API ou delegação ao Claude)
│   │   ├── notion_claude_delegate.py   # subprocess `claude -p` para MCP Notion
│   │   ├── notion_publish_claude_tool.py # SRS -> Notion via `claude -p` (MCP)
│   │   ├── notion_publish_verify_claude_tool.py # auditoria de completude pós-publicação (MCP)
│   │   ├── notion_search_tool.py       # pesquisa REST Notion
│   │   ├── notion_page_comment_tool.py # comentários REST em páginas
│   │   ├── notion_publish_page_tool.py   # criação REST opcional (não usada pelo crew de publicação)
│   │   ├── notion_api_common.py
│   │   ├── repo_read_tool.py
│   │   ├── workflow_output_read_tool.py
│   │   ├── briefing_file_tool.py
│   │   ├── srs_publish_read_tool.py    # leitura do SRS no fluxo de publicação
│   │   ├── meeting_transcript_read_tool.py        # atualização SRS por reunião — transcrição
│   │   ├── meeting_update_artifact_read_tool.py   # atualização SRS por reunião — releitura
│   │   ├── notion_publish_artifact_read_tool.py   # releitura do plano/log da publicação Notion
│   │   ├── notion_collect_page_comments_claude_tool.py # varredura de comentários (MCP)
│   │   ├── notion_apply_srs_changes_claude_tool.py # aplica o diff aprovado via MCP
│   │   ├── notion_update_versions_claude_tool.py   # atualiza página Notion de Versões
│   │   └── srs_versions_local_update_tool.py       # append idempotente da nova versão no SRS local
│   ├── llm_defaults.py                 # API vs CLI do LLM + bootstrap opcional do HOME
│   ├── claude_code_llm.py              # BaseLLM CrewAI -> `claude -p`
│   ├── crew.py                         # ArvoAuthOrchestrator
│   ├── srs_crew.py                     # SrsAuthorCrew
│   ├── notion_publish_crew.py          # SrsNotionPublishCrew
│   ├── notion_gap_comment_crew.py      # NotionGapCommentCrew
│   ├── srs_meeting_update_crew.py      # SrsMeetingChangesPlanCrew + SrsMeetingChangesApplyCrew
│   ├── srs_notion_diff_apply_crew.py   # SrsNotionDiffApplyCrew (só diff, sem Versões)
│   └── main.py                         # … run_srs_meeting_update, run_srs_meeting_update_apply, …
├── .env.example
├── pyproject.toml                      # … run_srs_meeting_update, run_srs_meeting_update_apply, …
├── README.md                           # inglês
└── README.pt-BR.md                     # este arquivo
```

---

## Claude Code (local)

No **modo API**, mantenha **`MODEL`** e **`ANTHROPIC_API_KEY`** alinhados ao projeto Anthropic. No **modo CLI**, o modelo segue a instalação do Claude Code (`CLAUDE_CODE_EXTRA_ARGS`, etc.). Opcional: [skills CrewAI para Claude Code](https://docs.crewai.com/en/guides/coding-tools/build-with-ai) (`/plugin marketplace add crewAIInc/skills`).

---

## Solução de problemas

| Problema | O que fazer |
| --- | --- |
| Erros de `onnxruntime` / plataforma no `uv sync` | `[tool.uv] override-dependencies` no `pyproject.toml`; ajuste o pin se necessário. |
| `unable to open database file` (SQLite do CrewAI) | Defina `ARVO_CREWAI_IN_PROJECT_HOME=1` para gravar estado em `.crewai_runtime_home/`. |
| Notion 400 ao criar página | Confirme que a integração tem acesso a `NOTION_SRS_PARENT_PAGE_ID`; verifique o nome da propriedade de título vs. idioma do workspace. |
| Notion **403** em `run_notion_gap_comments` | Ative capacidades de **comentário** e pesquisa na integração; confira `NOTION_API_KEY`. |

---

## Referências

- [Documentação CrewAI](https://docs.crewai.com/)
- [CrewAI — LLMs / Anthropic](https://docs.crewai.com/en/concepts/llms)
- [Notion API — Criar página](https://developers.notion.com/reference/post-page)
