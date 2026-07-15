# Crew: decomposição SRS → Linear — copilot (`CopilotLinearTasksCreationCrew`)

Variante do [`LinearTasksCreationCrew`](crew-linear-tasks-creation.md) para o time **copilot**.

## Identificação

| Campo | Valor |
| --- | --- |
| **Time** | `copilot` |
| **Classe** | `CopilotLinearTasksCreationCrew` |
| **Ficheiro** | `src/arvo_auth/copilot/linear_tasks_crew.py` |
| **Comando** | `uv run run_copilot_linear_tasks` |

## Objetivo

Ler o SRS publicado no Notion (dashboard copilot) e criar uma **árvore de issues no Linear** (Issue Pai + sub-issues Backend/Frontend/Infra), dimensionada para implementação autónoma por IA.

## Fluxo típico end-to-end

```bash
uv run run_copilot_srs
uv run run_copilot_notion_publish
uv run run_copilot_linear_tasks
```

## Variáveis de ambiente

| Variável | Obrigatório | Descrição |
| --- | --- | --- |
| `ARVO_COPILOT_SRS_NOTION_PAGE_URL` | Sim | URL completa da página Dashboard SRS no Notion (fallback: `ARVO_SRS_NOTION_PAGE_URL`) |
| `ARVO_COPILOT_SRS_NOTION_PAGE_ID` | Legado | UUID (aceito; convertido para URL internamente) |
| `ARVO_COPILOT_LINEAR_TEAM_KEY` | Sim | Key do time Linear (fallback: `ARVO_LINEAR_TEAM_KEY`, e.g. `COP`) |
| `ARVO_COPILOT_LINEAR_PROJECT_URL` | Opcional | URL do project Linear (fallback: `ARVO_LINEAR_PROJECT_URL`) |
| `ARVO_COPILOT_LINEAR_PROJECT_ID` | Legado | UUID/short id (aceito se URL não estiver definida) |
| `ARVO_COPILOT_LINEAR_PROJECT_NAME` | Legado | Nome do project (aceito se URL não estiver definida) |
| `ARVO_COPILOT_SRS_PROJECT_NAME`, `ARVO_COPILOT_SRS_PHASE` | Não | Interpolação nos prompts (fallback `ARVO_SRS_*`) |
| `ARVO_LINEAR_DELEGATE_TIMEOUT_SEC` | Não | Timeout do subprocess `claude -p` por issue (default `180`) |
| `CLAUDE_CODE_PERMISSION_MODE` | Recomendado | `bypassPermissions` para criação automática via MCP |

## Saídas

| Ficheiro |
| --- |
| `outputs/copilot/linear_tasks_creation/01_srs_content.md` |
| `outputs/copilot/linear_tasks_creation/02_issues_draft.json` |
| `outputs/copilot/linear_tasks_creation/03_publish_log.md` |

## Referências

- Base: `src/arvo_auth/core/linear_tasks_crew_base.py`
- Config: `src/arvo_auth/core/linear_tasks_config.py`
- Engineering (referência): [crew-linear-tasks-creation.md](crew-linear-tasks-creation.md)
