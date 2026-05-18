# Crew: comentários Notion para lacunas e conflitos (`NotionGapCommentCrew`)

## Identificação

| Campo | Valor |
| --- | --- |
| **Classe** | `NotionGapCommentCrew` |
| **Ficheiro** | `src/arvo_auth_orchestrator/notion_gap_comment_crew.py` |
| **Configuração** | `config/notion_gap_comment_agents.yaml`, `config/notion_gap_comment_tasks.yaml` |
| **Processo** | Sequencial |
| **Comando** | `uv run run_notion_gap_comments` |
| **Entrada em código** | `main.run_notion_gap_comments()` |

## Objetivo

Percorrer **lacunas e conflitos ativos** descritos nos artefactos locais (prioridade: `outputs/srs_workflow/gaps_and_open_questions.md`), usar a **API REST Notion** para **pesquisar páginas** relevantes e publicar **comentários** na página com **perguntas de esclarecimento** — sem criar novas páginas e sem usar o fluxo MCP `claude -p` da publicação SRS.

## O que faz

1. **Passo A — Manifesto**  
   O agente lê artefactos do workflow (`read_workflow_artifact`: `gaps_and_open_questions.md`, opcionalmente `SRS.md`, `product.md`, `overview.md`) e, se útil, ficheiros do second-brain (`read_second_brain_file`, p.ex. `open-questions/index.md`). Produz uma tabela com IDs (G*, OQ-*), tipo (lacuna/conflito), queries de pesquisa e rascunho de perguntas. Saída: `outputs/notion_gap_comments/gap_comment_manifest.md`.

2. **Passo B — Pesquisa e comentários**  
   Para cada linha do manifesto (até ao limite configurado), chama `notion_search_pages`, escolhe o `page_id` mais plausível e `notion_post_page_comment` com markdown **inline** (limitações da API de comentários). Regista SKIPPED quando não há página adequada. Saída: `outputs/notion_gap_comments/gap_comment_execution_log.md`.

## Agente e ferramentas

| Agente | Ferramentas |
| --- | --- |
| **notion_gap_commenter** | `read_workflow_artifact`, `read_second_brain_file`, `notion_search_pages`, `notion_post_page_comment` |

Identidade em runtime: `knowledge/notion_gap_commenter_identity.md`.

## Variáveis de ambiente

| Variável | Obrigatório | Descrição |
| --- | --- | --- |
| `NOTION_API_KEY` | Sim | Token da integração com capacidade de **pesquisa** e **inserir comentários** (developer portal Notion). |
| `ARVO_GAP_COMMENT_MAX_ITEMS` | Não | Máximo de itens a processar por corrida (default `15`). |
| `ARVO_GAP_COMMENT_DRY_RUN` | Não | `1` / `true` / `yes` — não publica comentários; só simula no output da ferramenta. |
| `ARVO_GAP_COMMENT_SOURCES_HINT` | Não | Texto livre passado ao crew (prioridades, palavras-chave extra, caminhos). |
| `ARVO_SRS_PROJECT_NAME`, `ARVO_SRS_PHASE` | Não | Interpolação nas tarefas (igual aos outros crews). |
| `ARVO_SECOND_BRAIN_ROOT` | Não | Raiz do second-brain para `read_second_brain_file`. |

## Pré-requisitos Notion

- A integração deve ter acesso de leitura ao espaço onde estão as páginas SRS/publicação.
- Em **Connection capabilities**, ativar permissões para **comentários** (insert), caso contrário `notion_post_page_comment` devolve HTTP 403.

## Referências no repositório

- Ferramentas: `tools/notion_search_tool.py`, `tools/notion_page_comment_tool.py`
- Leitura de artefactos: `tools/workflow_output_read_tool.py` (inclui `gaps_and_open_questions.md` e `SRS.md`)
