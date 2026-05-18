# Documentação do Arvo Auth CrewAI

Índice da documentação por **crew** (CrewAI):

| Documento | Crew | Comando típico |
| --- | --- | --- |
| [crew-sdlc-pipeline.md](crews/crew-sdlc-pipeline.md) | `ArvoAuthOrchestrator` | `crewai run` |
| [crew-srs-author.md](crews/crew-srs-author.md) | `SrsAuthorCrew` | `uv run run_srs` · `uv run run_srs_replay` |
| [crew-srs-notion-publish.md](crews/crew-srs-notion-publish.md) | `SrsNotionPublishCrew` | `uv run run_notion_publish` |
| [crew-notion-gap-comments.md](crews/crew-notion-gap-comments.md) | `NotionGapCommentCrew` | `uv run run_notion_gap_comments` |
| [crew-srs-meeting-update.md](crews/crew-srs-meeting-update.md) | `SrsMeetingChangesPlanCrew` (+ opcional `SrsMeetingChangesApplyCrew`) | `uv run run_srs_meeting_update` · `uv run run_srs_meeting_update_apply` |
| [crew-srs-notion-diff-apply.md](crews/crew-srs-notion-diff-apply.md) | `SrsNotionDiffApplyCrew` | `uv run run_srs_notion_diff_apply` |

Visão geral de instalação e variáveis: [README.md](../README.md) (EN) e [README.pt-BR.md](../README.pt-BR.md) (pt-BR).
