# Crew: autor de SRS copilot (`CopilotSrsAuthorCrew`)

## Identificação

| Campo | Valor |
| --- | --- |
| **Time** | `copilot` |
| **Classe** | `CopilotSrsAuthorCrew` |
| **Ficheiro** | `src/arvo_auth/copilot/srs_crew.py` |
| **Configuração** | `copilot/config/srs_agents.yaml`, `copilot/config/srs_tasks.yaml` |
| **Comando** | `uv run run_copilot_srs` · `uv run run_copilot_srs_replay` |
| **Entrada em código** | `main.run_copilot_srs()`, `main.run_copilot_srs_replay()` |

## Objetivo

Mesmo pipeline do [`SrsAuthorCrew`](crew-srs-author.md) (engineering): overview de produto → memórias intermediárias → `SRS.md`, com outputs isolados em `outputs/copilot/srs_workflow/`.

O `SRS.md` final é um **contrato autossuficiente** para engenharia, QA e auditoria: o agente lê os sete artefatos intermediários em disco, mas o documento publicado **não** os cita.

## Formato do `SRS.md` final

| Regra | Detalhe |
| --- | --- |
| Estrutura | Seções **1–7** apenas (Introdução → Revisão Crítica IEEE 1012-2024) |
| Introdução | `1.1` Propósito · `1.2` Escopo · `1.3` Definições · `1.4` **Visão Geral do Documento** (não «Referências») |
| Proibido no corpo | Seção de referências a artefatos do workflow; notas `*Rastreabilidade:*`; matriz de rastreabilidade a ficheiros `.md`; preâmbulo meta; rodapé de proveniência |
| Artefatos passos 1–6 | Permanecem em `outputs/copilot/srs_workflow/` como **entrada** do crew — não são anexos do SRS entregue |

Política codificada em `copilot/knowledge/srs_authoring_rules.md`, `srs_author_identity.md` e na tarefa `author_srs_task` (`srs_tasks.yaml`). Plano: `plans/copilot_srs_author/plano.md` (critério de aceite #6).

## Diferenças vs engineering

| Aspeto | Engineering | Copilot |
| --- | --- | --- |
| Outputs | `outputs/engineering/srs_workflow/` | `outputs/copilot/srs_workflow/` |
| Knowledge / regras | `engineering/knowledge/` | `copilot/knowledge/` |
| Env kickoff | `ARVO_SRS_*` | `ARVO_COPILOT_SRS_*` (fallback opcional para `ARVO_SRS_*`) |
| Replay task id | `ARVO_SRS_REPLAY_TASK_ID` | `ARVO_COPILOT_SRS_REPLAY_TASK_ID` |
| Repos (código) | `ARVO_*_REPO_ROOT` | **Mesmas variáveis** — apontar para repos copilot |

## Variáveis de ambiente (kickoff)

| Variável | Obrigatório | Descrição |
| --- | --- | --- |
| `ARVO_COPILOT_SRS_OVERVIEW_FILE` ou `ARVO_COPILOT_SRS_PRODUCT_OVERVIEW` | Sim (recomendado ficheiro) | Overview; fallback para `ARVO_SRS_*` se vazio |
| `ARVO_COPILOT_SRS_BRIEFING_FILE` | Opcional | Markdown extra (preferido para briefings longos) |
| `ARVO_COPILOT_SRS_BRIEFING_MARKDOWN` | Opcional | Inline se `BRIEFING_FILE` não definido |
| `ARVO_COPILOT_SRS_RULES_FILE` | Opcional | Default `srs_authoring_rules.md` em `copilot/knowledge/` |
| `ARVO_COPILOT_SRS_PROJECT_NAME` | Opcional | Default `Arvo Copilot` |
| `ARVO_COPILOT_SRS_PHASE` | Opcional | Fase do produto |
| `ARVO_BACKEND_REPO_ROOT`, `ARVO_FRONTEND_REPO_ROOT`, `ARVO_INFRA_REPO_ROOT` | Recomendado | Raízes locais dos repos copilot |
| `ARVO_SECOND_BRAIN_ROOT`, `NOTION_PAGE_IDS` | Opcional | Igual ao engineering |
| `ARVO_COPILOT_SRS_REPLAY_TASK_ID` | Replay | UUID da tarefa `author_srs_task` |

## Saídas

| Ficheiro | Passo |
| --- | --- |
| `outputs/copilot/srs_workflow/step_01_ingest_memory.md` | 1 |
| `outputs/copilot/srs_workflow/overview.md` | 2 |
| `outputs/copilot/srs_workflow/product_research_notes.md` | 3 |
| `outputs/copilot/srs_workflow/product.md` | 4 |
| `outputs/copilot/srs_workflow/repo_analysis.md` | 5 |
| `outputs/copilot/srs_workflow/backend.md` | 6a |
| `outputs/copilot/srs_workflow/frontend.md` | 6b |
| `outputs/copilot/srs_workflow/infra.md` | 6c |
| `outputs/copilot/srs_workflow/SRS.md` | 7 — documento final **autossuficiente** (seções 1–7; sem referências aos artefatos intermediários) |

## Referências

- Base partilhada: `src/arvo_auth/core/srs_author_crew_base.py`
- Inputs: `src/arvo_auth/core/srs_inputs.py`
- Plano: `plans/copilot_srs_author/plano.md`
