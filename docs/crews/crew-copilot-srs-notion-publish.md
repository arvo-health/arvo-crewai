# Crew: publicação SRS no Notion — copilot (`CopilotSrsNotionPublishCrew`)

Variante do [`SrsNotionPublishCrew`](crew-srs-notion-publish.md) para o time **copilot**.

## Identificação

| Campo | Valor |
| --- | --- |
| **Time** | `copilot` |
| **Classe** | `CopilotSrsNotionPublishCrew` |
| **Ficheiro** | `src/arvo_auth/copilot/notion_publish_crew.py` |
| **Comando** | `uv run run_copilot_notion_publish` |

## Fluxo típico

```bash
uv run run_copilot_srs
uv run run_copilot_notion_publish
```

## Entradas

| Variável | Descrição |
| --- | --- |
| `ARVO_COPILOT_SRS_PUBLISH_INPUT` | Path do SRS (fallback: `ARVO_SRS_PUBLISH_INPUT`; default: `outputs/copilot/srs_workflow/SRS.md`) |
| `NOTION_COPILOT_SRS_PARENT_PAGE_ID` | UUID da página pai (fallback: `NOTION_SRS_PARENT_PAGE_ID`) |
| `NOTION_COPILOT_SRS_PARENT_URL` | URL da página pai (fallback: `NOTION_SRS_PARENT_URL`) |
| `ARVO_COPILOT_SRS_PROJECT_NAME`, `ARVO_COPILOT_SRS_PHASE` | Interpolação nos prompts (fallback `ARVO_SRS_*`) |

## Saídas

| Ficheiro |
| --- |
| `outputs/copilot/notion_export/publish_plan.md` |
| `outputs/copilot/notion_export/publish_execution_log.md` |
| `outputs/copilot/notion_export/publish_completeness_review.md` |

## Referências

- Base: `src/arvo_auth/core/notion_publish_crew_base.py`
- Config: `src/arvo_auth/core/srs_notion_publish_config.py`
