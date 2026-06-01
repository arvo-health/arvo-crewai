# Documentação do Arvo Auth CrewAI

Índice da documentação por **crew** (CrewAI), agrupada por time.

## Time de engenharia

| Documento | Crew | Comando típico |
| --- | --- | --- |
| [crew-sdlc-pipeline.md](crews/crew-sdlc-pipeline.md) | `ArvoAuthOrchestrator` | `crewai run` |
| [crew-srs-author.md](crews/crew-srs-author.md) | `SrsAuthorCrew` | `uv run run_srs` · `uv run run_srs_replay` |
| [crew-srs-notion-publish.md](crews/crew-srs-notion-publish.md) | `SrsNotionPublishCrew` | `uv run run_notion_publish` |
| [crew-linear-tasks-creation.md](crews/crew-linear-tasks-creation.md) | `LinearTasksCreationCrew` | `uv run run_linear_tasks` |
| [crew-notion-gap-comments.md](crews/crew-notion-gap-comments.md) | `NotionGapCommentCrew` | `uv run run_notion_gap_comments` |
| [crew-srs-meeting-update.md](crews/crew-srs-meeting-update.md) | `SrsMeetingChangesPlanCrew` (+ opcional `SrsMeetingChangesApplyCrew`) | `uv run run_srs_meeting_update` · `uv run run_srs_meeting_update_apply` |
| [crew-srs-notion-diff-apply.md](crews/crew-srs-notion-diff-apply.md) | `SrsNotionDiffApplyCrew` | `uv run run_srs_notion_diff_apply` |
| [crew-frontend-branch-mapping.md](crews/crew-frontend-branch-mapping.md) | `FrontendBranchMappingCrew` | `uv run run_frontend_branch_mapping` |
| [crew-service-handover.md](crews/crew-service-handover.md) | `ServiceHandoverCrew` | `uv run run_service_handover` |

## Time de data science

| Documento | Crew | Status | Comando típico |
| --- | --- | --- | --- |
| [crew-ds-experiment-spec.md](crews/crew-ds-experiment-spec.md) | `ExperimentSpecCrew` | Implementado | `uv run run_ds_experiment_spec` |
| [crew-ds-solution-architecture.md](crews/crew-ds-solution-architecture.md) | `SolutionArchitectureCrew` | Planejado | _(futuro)_ `uv run run_ds_solution_architecture` |
| [crew-ds-linear-sync.md](crews/crew-ds-linear-sync.md) | `LinearSyncCrew` | Planejado | _(futuro)_ `uv run run_ds_linear_sync` |

## Time copilot

Automação de fluxos para assistentes de código (Cursor, Claude Code). Artefatos em `outputs/copilot/`.

| Documento | Crew | Status | Comando típico |
| --- | --- | --- | --- |
| [crew-copilot-srs-author.md](crews/crew-copilot-srs-author.md) | `CopilotSrsAuthorCrew` | Implementado | `uv run run_copilot_srs` · `uv run run_copilot_srs_replay` |
| [crew-copilot-srs-notion-publish.md](crews/crew-copilot-srs-notion-publish.md) | `CopilotSrsNotionPublishCrew` | Implementado | `uv run run_copilot_notion_publish` |
| [crew-copilot-linear-tasks.md](crews/crew-copilot-linear-tasks.md) | `CopilotLinearTasksCreationCrew` | Implementado | `uv run run_copilot_linear_tasks` |

Para adicionar outro crew: [como-criar-um-flow.md](como-criar-um-flow.md).

Visão geral de instalação e variáveis: [README.md](../README.md) (EN) e [README.pt-BR.md](../README.pt-BR.md) (pt-BR).

## Guias

| Documento | Descrição |
| --- | --- |
| [como-criar-um-flow.md](como-criar-um-flow.md) | Passo a passo para criar um novo flow do zero |
