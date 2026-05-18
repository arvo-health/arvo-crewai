# Como Criar um Flow

Um **flow** é uma sequência de crews que, executados em ordem, entregam um objetivo de ponta a ponta. Cada crew gera artefatos em disco que o próximo crew consome. O usuário é o ponto de controle entre as etapas.

---

## Passo 1 — Defina o objetivo do flow

Antes de criar qualquer crew, responda:

- Qual é a entrada inicial do flow? (ex: transcrição de reunião, visão de produto)
- Qual é o artefato final esperado? (ex: `SRS.md`, páginas publicadas no Notion)
- Quais são os pontos de decisão humana? (ex: revisão de diff antes de aplicar)

Cada ponto de decisão humana é um corte natural entre dois crews.

---

## Passo 2 — Decomponha o flow em crews

Mapeie cada etapa autônoma como um crew separado. Um crew deve:

- Ter uma única responsabilidade (SRP)
- Receber entradas apenas de artefatos em disco ou variáveis de ambiente
- Produzir um ou mais artefatos em disco como saída

**Exemplo — Flow de Atualização SRS por Reunião:**

```
Entrada: transcript.md
  │
  ▼
[Crew: SrsMeetingChangesPlanCrew]
  └─ Saída: notion_changes_diff.md
  │
  ▼ [checkpoint humano: revisar o diff]
  │
  ▼
[Crew: SrsNotionDiffApplyCrew]
  └─ Saída: diff_apply_execution_log.md
```

---

## Passo 3 — Crie os agentes do crew

Para cada crew, defina os agentes em `config/<nome>_agents.yaml`:

```yaml
nome_do_agente:
  role: >
    Papel claro e específico do agente
  goal: >
    Objetivo mensurável que o agente deve atingir
  backstory: >
    Contexto, restrições e estilo de raciocínio do agente
```

Regras:
- Um agente por responsabilidade (SRP)
- `backstory` define identidade — use um knowledge file externo quando o conteúdo for longo (ver Passo 6)
- `goal` deve ser verificável: o agente sabe quando terminou

---

## Passo 4 — Defina as tarefas do crew

Para cada agente, defina as tarefas em `config/<nome>_tasks.yaml`:

```yaml
nome_da_tarefa:
  description: >
    Instrução detalhada do que o agente deve fazer.
    Referencie variáveis de entrada com {variavel}.
  expected_output: >
    Descrição precisa do artefato esperado (formato, localização, conteúdo mínimo).
  agent: nome_do_agente
```

Regras:
- Uma tarefa = um artefato de saída
- `expected_output` é contrato — o agente usa isso para saber quando a tarefa está completa
- Tarefas executam em sequência; cada uma acessa o contexto das anteriores

---

## Passo 5 — Implemente as tools necessárias

Tools são a interface entre o agente e o mundo externo.

**Tools compartilhadas** (reutilizáveis por qualquer time) ficam em `src/arvo_auth/core/tools/`.

**Tools específicas de um time** ficam dentro do próprio diretório do time (ex: `src/arvo_auth/<nome_do_time>/tools/`).

```python
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class MinhaToolInput(BaseModel):
    caminho: str = Field(description="Caminho do arquivo a ser lido")

class MinhaFileTool(BaseTool):
    name: str = "minha_file_tool"
    description: str = "Lê o conteúdo de um arquivo e retorna como string."
    args_schema: type[BaseModel] = MinhaToolInput

    def _run(self, caminho: str) -> str:
        with open(caminho, "r", encoding="utf-8") as f:
            return f.read()
```

Regras:
- Uma tool por responsabilidade
- `description` é lida pelo agente para decidir quando usar a tool — seja preciso
- Efeitos colaterais (escrita, API calls) devem estar isolados em tools, nunca em agentes
- Prefira reutilizar tools de `core/tools/` antes de criar novas

---

## Passo 6 — Crie o knowledge file do agente (opcional)

Quando o backstory do agente for longo ou reutilizável, extraia para `src/arvo_auth/<nome_do_time>/knowledge/<nome>_identity.md`:

```markdown
Você é um especialista em [domínio].

Suas responsabilidades:
- [responsabilidade 1]
- [responsabilidade 2]

Restrições:
- [restrição 1]
- [restrição 2]
```

Injete no crew via `knowledge_sources` ou interpolando no campo `backstory` do YAML.

---

## Passo 7 — Implemente a classe do crew

Crie o arquivo do crew em `src/arvo_auth/<nome_do_time>/<nome>_crew.py`:

```python
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from arvo_auth.core.llm_defaults import default_llm
from arvo_auth.core.tools.minha_file_tool import MinhaFileTool  # tool compartilhada
# ou, para tool específica do time:
# from arvo_auth.<nome_do_time>.tools.minha_file_tool import MinhaFileTool

@CrewBase
class MeuCrew:
    agents_config = "config/meu_crew_agents.yaml"
    tasks_config  = "config/meu_crew_tasks.yaml"

    @agent
    def meu_agente(self) -> Agent:
        return Agent(
            config=self.agents_config["meu_agente"],
            tools=[MinhaFileTool()],
            llm=default_llm(),
            verbose=True,
        )

    @task
    def minha_tarefa(self) -> Task:
        return Task(config=self.tasks_config["minha_tarefa"])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
```

---

## Passo 8 — Registre o entry point CLI

Em `src/arvo_auth/main.py`, adicione a função de entrada:

```python
def run_meu_flow():
    from arvo_auth.<nome_do_time>.meu_crew import MeuCrew
    root = _project_root()
    (root / "outputs" / "<nome_do_time>" / "meu_workflow").mkdir(parents=True, exist_ok=True)
    MeuCrew().crew().kickoff(inputs={
        "variavel": os.getenv("MINHA_VARIAVEL", "valor_padrao"),
    })
```

Em `pyproject.toml`, registre o comando:

```toml
[project.scripts]
run_meu_flow = "arvo_auth.main:run_meu_flow"
```

Após isso, execute com:

```bash
uv run run_meu_flow
```

---

## Passo 9 — Documente o crew

Crie `docs/crews/crew-<nome>.md` seguindo a estrutura dos crews existentes:

- Identificação (classe, comando, arquivo)
- Objetivo
- O que faz (lista de tarefas e artefatos)
- Agentes
- Artefatos necessários (entradas)
- Variáveis de ambiente
- Saídas geradas
- Diagrama Mermaid do fluxo de tarefas
- Referências no repositório

Adicione o link em `docs/README.md`.

---

## Checklist de Validação

Antes de considerar o flow completo:

- [ ] Cada crew tem responsabilidade única e bem definida
- [ ] Entradas e saídas de cada crew são artefatos em disco (sem acoplamento direto entre crews)
- [ ] Checkpoints humanos identificados e documentados
- [ ] Todas as variáveis de ambiente documentadas em `docs/crews/`
- [ ] Knowledge files criados para agentes com backstory extenso
- [ ] Entry point registrado em `pyproject.toml`
- [ ] Documentação criada em `docs/crews/` com diagrama Mermaid
- [ ] Link adicionado em `docs/README.md`
