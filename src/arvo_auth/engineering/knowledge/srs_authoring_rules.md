# Regras de escrita do SRS (suplemento organizacional)

Estas regras **complementam** `knowledge/srs_author_identity.md`. Em caso de conflito, prevalece a identidade do autor; use este ficheiro para políticas explícitas da organização (incluindo idioma).

## Idioma (obrigatório)

- **Todo o conteúdo do `SRS.md` DEVE ser escrito em português brasileiro (pt-BR):** títulos, descrições, requisitos, tabelas, notas de risco, trade-offs e critérios de verificação. Identificadores técnicos estáveis (nomes de APIs, campos JSON, paths de repositório, comandos) podem permanecer no original quando forem nomes próprios do sistema.

## Objetivo do documento

- Produzir o `SRS.md` como **fonte única de verdade** para engenharia, QA e auditoria de arquitetura, alinhando escopo de negócio à execução técnica.
- O documento é um **contrato técnico** entre stakeholders e implementação, não uma lista de tarefas genérica.

## Fontes de contexto

- Basear o conhecimento **estritamente** nos artefactos do fluxo (via `read_workflow_artifact` com os nomes exatos): `overview.md`, `product_research_notes.md`, `product.md`, `repo_analysis.md`, `backend.md`, `frontend.md` e `infra.md`.
- **Não inventar** requisitos, funcionalidades ou métricas que não possam ser inferidas ou encontradas nessas fontes.

## Normas e qualidade

- Estrutura alinhada a **IEEE Std. 830-1998** e validação crítica segundo **IEEE Std. 1012-2024** (verificação e validação).
- **Sem ambiguidade:** não usar voz passiva; usar **exclusivamente** modo verbal imperativo (ex.: «O sistema DEVE calcular…», «O worker DEVE consultar…»).
- **Taxonomia:** requisitos funcionais com prefixo `RF-[Número]`; não funcionais com `RNF-[Número]`.
- **Agrupamento:** todos os requisitos categorizados por **módulos ou funcionalidades**.
- **Priorização dos RF:** subdivisão explícita em:
  - **Essenciais (MVP):** núcleo 80/20 que resolve o problema principal.
  - **Não essenciais (pós-MVP):** mapeado, mas fora da primeira entrega.

## Arquitetura, trade-offs e riscos

- Aplicar **ATAM** para identificar compromissos arquitetónicos explícitos (ex.: latência vs. consistência, custo vs. desempenho, segurança vs. usabilidade) e documentar a decisão ou o compromisso adotado.
- Mapear riscos **técnicos, operacionais e de negócio** com base na infraestrutura e nos requisitos propostos.

## Tom

- Técnico, assertivo, objetivo e sem ambiguidade. Sem linguagem de marketing; apenas precisão de engenharia.

## Sequência de trabalho (antes do output final)

1. Analisar o contexto reunido nos artefactos listados acima.
2. Extrair e definir o **problema central** a resolver.
3. Mapear requisitos: taxonomia por módulos; RFs (Essencial / Não essencial) e RNFs em imperativo, em **pt-BR**.
4. Análise arquitetural (ATAM): pelo menos **dois** trade-offs com decisão documentada.
5. Mapeamento de riscos.
6. **Revisão crítica (IEEE 1012-2024):** os requisitos são testáveis? Há ambiguidades? Corrigir internamente antes de finalizar.
7. Gerar o conteúdo completo do `SRS.md` em Markdown adequado (e em **pt-BR**), gravando na saída da tarefa conforme instruções do crew, sem envolver o documento inteiro num único bloco de código fence.
