# Crew: aplicar diff Notion (só operações do diff)

## Identificação

| Campo | Valor |
| --- | --- |
| **Classe** | `SrsNotionDiffApplyCrew` |
| **Ficheiro** | `src/arvo_auth_orchestrator/srs_notion_diff_apply_crew.py` |
| **Configuração** | `config/srs_notion_diff_apply_agents.yaml`, `config/srs_notion_diff_apply_tasks.yaml` |
| **Processo** | Sequencial (uma tarefa) |
| **Comando** | `uv run run_srs_notion_diff_apply` |
| **Entrada em código** | `main.run_srs_notion_diff_apply()` |

## Objetivo

Aplicar ao Notion, num único subprocesso MCP (`notion_apply_srs_changes_via_claude`), as operações descritas em `outputs/srs_meeting_update/notion_changes_diff.md`. **Não** atualiza a secção Versões/Atualizações no `SRS.md` local nem na página Notion correspondente.

## Relação com outros crews

| Fluxo | Comando | Versões |
| --- | --- | --- |
| Só aplicar o diff no Notion | `uv run run_srs_notion_diff_apply` | Não |
| Diff + Versões (meeting update completo) | `uv run run_srs_meeting_update_apply` | Sim |

## Agente e ferramentas

| Agente | Ferramentas |
| --- | --- |
| **notion_diff_applier** | `notion_apply_srs_changes_via_claude` |

Identidade: `knowledge/srs_notion_diff_applier_identity.md`.

## Variáveis de ambiente

| Variável | Obrigatório | Descrição |
| --- | --- | --- |
| `NOTION_SRS_PARENT_PAGE_ID` / `NOTION_SRS_PARENT_URL` | Sim | Raiz do workspace Notion |
| `NOTION_APPLY_CHANGES_CLAUDE_TIMEOUT_SEC` | Opcional | Timeout do subprocesso (default 1800 s) |

## Saídas

| Ficheiro | Descrição |
| --- | --- |
| `outputs/srs_meeting_update/diff_apply_execution_log.md` | Resultado `APPLY_*` + resumo |

O diff lido é sempre `outputs/srs_meeting_update/notion_changes_diff.md` (mesmo caminho que o crew de plano de meeting update gera).

## Referências

- Ferramenta: `src/arvo_auth_orchestrator/tools/notion_apply_srs_changes_claude_tool.py`
- Plano (second-brain): `second-brain/plans/backend/arvo-auth-orchestrator/crew-srs-notion-diff-apply.md`
