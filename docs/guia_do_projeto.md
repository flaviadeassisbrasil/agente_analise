# Guia Completo do Projeto DataLens

> Este documento explica tudo que foi criado no scaffold do projeto, o que é LangGraph,
> por que escolhemos essa arquitetura e como cada peça se encaixa.
> Escrito para quem está chegando agora no projeto sem experiência prévia com LangGraph.

---

## Índice

1. [O que o projeto faz](#1-o-que-o-projeto-faz)
2. [O que é LangGraph e por que usamos](#2-o-que-é-langgraph-e-por-que-usamos)
3. [Conceitos centrais do LangGraph](#3-conceitos-centrais-do-langgraph)
4. [O fluxo completo do agente](#4-o-fluxo-completo-do-agente)
5. [Estrutura de pastas explicada](#5-estrutura-de-pastas-explicada)
6. [Cada arquivo em detalhe](#6-cada-arquivo-em-detalhe)
7. [Como rodar localmente](#7-como-rodar-localmente)
8. [O que ainda falta implementar](#8-o-que-ainda-falta-implementar)

---

## 1. O que o projeto faz

O DataLens é um agente inteligente que:

1. **Recebe um arquivo** do usuário (CSV, Excel, JSON, PDF ou DOCX)
2. **Lê e interpreta** o conteúdo desse arquivo
3. **Analisa os dados** — estatísticas, padrões, anomalias
4. **Gera visualizações** — gráficos interativos
5. **Produz um relatório** estruturado pronto para decisão
6. **Responde perguntas** sobre os dados via chat

Tudo isso acontece através de uma interface web simples feita com Streamlit.

---

## 2. O que é LangGraph e por que usamos

### A alternativa que descartamos: LangChain AgentExecutor

O LangChain tem um componente chamado `AgentExecutor` que funciona assim:

```
usuário pergunta → LLM decide qual tool usar → tool executa → LLM decide de novo → ...repete até parar
```

Parece simples, mas o problema é que **você não controla o fluxo**. O LLM decide sozinho quando parar, em que ordem chamar as ferramentas, e se algo der errado é difícil de diagnosticar. Para um agente de análise de dados, onde a ordem importa (primeiro lê, depois analisa, depois gera gráfico), isso é um problema.

### O que o LangGraph faz diferente

O LangGraph resolve isso deixando **você** definir o fluxo como um **grafo dirigido**:

```
você define: parse SEMPRE vem antes de profile
             profile SEMPRE vem antes de analyze
             analyze SEMPRE vem antes de visualize
```

Em vez de uma caixa preta, você tem um mapa explícito de como o agente se comporta.

### Uma analogia simples

Imagine uma linha de produção de uma fábrica:

| Conceito LangGraph | Analogia da fábrica |
|---|---|
| **Estado (State)** | A caixa que passa pela esteira carregando o produto em construção |
| **Nó (Node)** | Uma estação da linha de produção (solda, pintura, inspeção) |
| **Aresta (Edge)** | A esteira que conecta uma estação à próxima |
| **Aresta Condicional** | Um desvio na esteira: "se o produto for metal → estação A, se for plástico → estação B" |
| **Grafo compilado** | A linha de produção completa pronta para funcionar |

No DataLens:
- A **caixa** é o `AgentState` — ela começa vazia e vai sendo preenchida a cada estação
- As **estações** são os nós: `parse`, `profile`, `analyze`, `visualize`, `report`, `chat`
- A **esteira** conecta os nós na ordem certa
- Os **desvios** decidem: "arquivo tabular → vai para profile / documento de texto → pula direto para analyze"

---

## 3. Conceitos centrais do LangGraph

### 3.1 O Estado (`AgentState`)

O estado é um dicionário tipado que representa **tudo que o agente sabe** em qualquer momento.
É definido em `src/agent/state.py`:

```python
class AgentState(TypedDict):
    messages: list          # histórico do chat
    file_path: str          # caminho do arquivo enviado pelo usuário
    file_type: str          # "csv", "excel", "json", "pdf" ou "docx"
    dataframe: DataFrame    # dados tabulares após leitura (CSV/Excel/JSON)
    raw_text: str           # texto extraído (PDF/DOCX)
    profile: dict           # estatísticas do dataset
    analysis: str           # análise gerada pelo Claude
    charts: list            # gráficos Plotly
    report: str             # relatório final em Markdown
    error: str              # mensagem de erro, se houver
```

**Regra fundamental:** nenhum nó modifica o estado diretamente. Cada nó **recebe** o estado atual e **retorna** um dicionário com apenas os campos que quer atualizar. O LangGraph faz o merge automaticamente.

```python
# ✅ correto — retorna só o que mudou
def profile_node(state: AgentState) -> AgentState:
    profile = profile_dataframe(state["dataframe"])
    return {**state, "profile": profile}

# ❌ errado — modificar o estado diretamente causa bugs
def profile_node(state: AgentState) -> AgentState:
    state["profile"] = profile_dataframe(state["dataframe"])  # não fazer isso
    return state
```

### 3.2 Os Nós (`Nodes`)

Cada nó é uma **função Python simples** que recebe o estado e retorna o estado atualizado.
Nada de mágica — é só uma função.

```python
def parse_node(state: AgentState) -> AgentState:
    # recebe o estado com file_path preenchido
    # detecta o tipo do arquivo
    # chama a tool de leitura correta
    # retorna o estado com dataframe OU raw_text preenchido
    ...
```

### 3.3 As Arestas (`Edges`)

Arestas conectam nós. Existem dois tipos:

**Aresta direta** — sempre vai para o mesmo próximo nó:
```python
graph.add_edge("profile", "analyze")
# profile SEMPRE vai para analyze, sem condição
```

**Aresta condicional** — decide o próximo nó com base no estado:
```python
def _route_after_parse(state: AgentState) -> str:
    if state.get("dataframe") is not None:
        return "profile"   # arquivo tabular → passa pelo profiling
    return "analyze"       # documento → pula direto para análise

graph.add_conditional_edges("parse", _route_after_parse, {
    "profile": "profile",
    "analyze": "analyze"
})
```

### 3.4 Compilação

Depois de definir todos os nós e arestas, você **compila** o grafo:

```python
graph = build_graph()  # retorna o grafo compilado e pronto para uso
```

A partir daí, você executa com:

```python
result = graph.invoke({
    "file_path": "/caminho/do/arquivo.csv",
    "messages": []
})
```

O LangGraph cuida de chamar cada nó na ordem certa, passando o estado atualizado de um para o outro.

---

## 4. O fluxo completo do agente

### Caso 1: Upload de novo arquivo tabular (CSV, Excel, JSON)

```
usuário faz upload de um CSV
         │
         ▼
    [ START ]
         │
         ▼ _route_entry: tem file_path e ainda não parseou → "parse"
    [ parse ]
    Detecta extensão → chama CSVTool
    Preenche: file_type="csv", dataframe=<DataFrame>
         │
         ▼ _route_after_parse: tem dataframe → "profile"
    [ profile ]
    Chama data_profiler → estatísticas, missing values, outliers
    Preenche: profile={shape, dtypes, missing, descriptive, anomalies, ...}
         │
         ▼ (aresta direta)
    [ analyze ]
    Envia profile para o Claude via langchain_anthropic
    Claude gera análise em texto estruturado
    Preenche: analysis="## Visão Geral\n..."
         │
         ▼ _route_after_analyze: tem dataframe → "visualize"
    [ visualize ]
    Gera histogramas, boxplots, scatter matrix com Plotly
    Preenche: charts=[fig1, fig2, fig3, ...]
         │
         ▼ (aresta direta)
    [ report ]
    Jinja2 renderiza o template com profile + analysis + chart_count
    Preenche: report="# Relatório DataLens\n..."
    Adiciona mensagem final ao histórico de chat
         │
         ▼
      [ END ]
```

### Caso 2: Upload de documento (PDF, DOCX)

```
usuário faz upload de um PDF
         │
         ▼
    [ START ]
         │
         ▼ _route_entry → "parse"
    [ parse ]
    Chama PDFTool → extrai texto
    Preenche: file_type="pdf", raw_text="..."
         │
         ▼ _route_after_parse: NÃO tem dataframe → "analyze"
    [ analyze ]                      ← pula o profile (sem tabela para perfilar)
    Envia raw_text para o Claude
    Preenche: analysis="..."
         │
         ▼ _route_after_analyze: NÃO tem dataframe → "report"
    [ report ]                       ← pula visualize (sem dados para graficar)
    Gera relatório
         │
         ▼
      [ END ]
```

### Caso 3: Pergunta no chat (arquivo já carregado)

```
usuário digita "qual é a média da coluna idade?"
         │
         ▼
    [ START ]
         │
         ▼ _route_entry: já tem dataframe/raw_text → "chat"
    [ chat ]
    Envia pergunta + estado atual (profile, dataframe) para o Claude
    Claude responde com base nos dados já carregados
    Adiciona resposta ao histórico de mensagens
         │
         ▼
      [ END ]
```

---

## 5. Estrutura de pastas explicada

```
agente_analisera/
│
├── app.py                          # Ponto de entrada — roda com "streamlit run app.py"
├── requirements.txt                # Dependências Python
├── .env.example                    # Template de variáveis de ambiente (copie para .env)
├── Makefile                        # Atalhos: make run, make test, make lint
├── pyproject.toml                  # Configuração de ferramentas (ruff, pytest)
│
├── src/                            # Todo o código da aplicação
│   │
│   ├── agent/                      # ← O CORAÇÃO DO PROJETO (LangGraph)
│   │   ├── state.py                # Define o AgentState (a "caixa" que circula)
│   │   ├── graph.py                # Monta o grafo: nós + arestas + roteamento
│   │   ├── nodes.py                # As funções de cada nó (parse, profile, analyze...)
│   │   └── prompts.py              # Prompts do sistema e templates para o Claude
│   │
│   ├── tools/                      # Ferramentas de leitura de arquivo
│   │   ├── base.py                 # Classe abstrata com validação comum
│   │   ├── csv_tool.py             # Lê CSV (detecta separador e encoding automaticamente)
│   │   ├── excel_tool.py           # Lê XLSX/XLS (suporta múltiplas abas)
│   │   ├── json_tool.py            # Lê JSON (achata estruturas nested em DataFrame)
│   │   ├── pdf_tool.py             # Extrai texto de PDF via PyMuPDF
│   │   ├── docx_tool.py            # Extrai texto e tabelas de DOCX
│   │   └── analysis_tool.py        # Estatísticas descritivas + detecção de outliers
│   │
│   ├── report/                     # Geração do relatório final
│   │   ├── charts.py               # Gráficos Plotly (histograma, boxplot, scatter)
│   │   ├── generator.py            # Orquestra a geração do relatório via Jinja2
│   │   └── templates/
│   │       └── report_template.md  # Template Markdown com variáveis Jinja2
│   │
│   └── utils/                      # Utilitários gerais
│       ├── file_handler.py         # Detecta tipo de arquivo, salva upload do Streamlit
│       └── data_profiler.py        # Monta o perfil completo do DataFrame
│
└── tests/                          # Testes automatizados
    ├── conftest.py                 # Fixtures reutilizáveis (gera arquivos de amostra)
    ├── fixtures/                   # Arquivos de teste estáticos
    ├── test_tools/
    │   ├── test_csv_tool.py        # 5 testes da CSVTool
    │   ├── test_excel_tool.py      # 2 testes da ExcelTool
    │   └── test_json_tool.py       # 2 testes da JSONTool
    └── test_agent/                 # Testes do agente (a implementar nas sprints)
```

---

## 6. Cada arquivo em detalhe

### `src/agent/state.py` — O estado do agente

É o arquivo mais importante para entender o LangGraph. Define o `AgentState`:
um `TypedDict` (dicionário com tipos definidos) que representa **o estado completo**
do agente em qualquer ponto da execução.

O campo `messages` tem um tratamento especial — usa `add_messages` do LangGraph,
que automaticamente **acumula** as mensagens em vez de sobrescrever.
Todos os outros campos são simplesmente sobrescritos quando um nó retorna um novo valor.

---

### `src/agent/graph.py` — O grafo

Aqui o grafo é **montado e compilado**. As três funções de roteamento (`_route_entry`,
`_route_after_parse`, `_route_after_analyze`) são as únicas que tomam decisões de fluxo.
Elas retornam uma string com o nome do próximo nó.

A função `build_graph()` é chamada uma única vez quando o app sobe.
O grafo compilado é então reutilizado para cada execução (`graph.invoke(...)`).

---

### `src/agent/nodes.py` — Os nós

Cada nó é uma função que faz uma coisa só:

| Nó | Entrada no estado | Saída no estado |
|---|---|---|
| `parse_node` | `file_path` | `file_type` + `dataframe` ou `raw_text` |
| `profile_node` | `dataframe` | `profile` |
| `analyze_node` | `profile` ou `raw_text` | `analysis` |
| `visualize_node` | `dataframe` + `profile` | `charts` |
| `report_node` | todos os anteriores | `report` + nova mensagem em `messages` |
| `chat_node` | `messages` + dados carregados | nova mensagem em `messages` |

> **Atenção:** `analyze_node` e `chat_node` têm `TODO` — é onde a chamada real ao Claude
> precisa ser implementada na Sprint 2.

---

### `src/agent/prompts.py` — Os prompts

Define os prompts do sistema e funções construtoras de prompt.
`SYSTEM_ANALYSIS` instrui o Claude a gerar análises estruturadas.
`SYSTEM_CHAT` instrui o Claude a responder perguntas sobre dados já carregados.
As funções `build_analysis_prompt` e `build_chat_prompt` constroem o prompt completo
a partir do estado — precisam ser implementadas na Sprint 2.

---

### `src/tools/base.py` — A classe base

Define a interface que **todas** as tools de leitura devem seguir:
um método `read(file_path)` e um método auxiliar `_validate_path` que checa
se o arquivo existe antes de tentar abrir.

Usar uma classe base garante que todas as tools têm o mesmo contrato,
facilitando o código do `parse_node` que simplesmente faz `reader.read(file_path)`.

---

### `src/tools/csv_tool.py` — Leitura de CSV

Tenta ler o CSV testando combinações de separadores (`,` `;` `\t` `|`) e encodings
(`utf-8`, `latin-1`, `cp1252`) até encontrar a combinação que produz mais de uma coluna.
Isso resolve a maioria dos CSVs "problemáticos" gerados por Excel brasileiro
(que usa `;` como separador e `latin-1` como encoding).

---

### `src/tools/json_tool.py` — Leitura de JSON

Usa `pd.json_normalize` que é a função do pandas para "achatar" JSONs aninhados.

Exemplo: um JSON assim:
```json
[{"id": 1, "user": {"name": "Alice", "age": 25}}]
```
vira um DataFrame com colunas `id`, `user.name`, `user.age`.

---

### `src/tools/analysis_tool.py` — Análise estatística

Duas funções independentes (não são uma classe — são funções simples):

- `describe_dataframe`: retorna shape, tipos, missing values, estatísticas descritivas e correlações
- `detect_anomalies`: usa o método IQR (Interquartile Range) para detectar outliers.
  Um valor é outlier se estiver abaixo de `Q1 - 1.5*IQR` ou acima de `Q3 + 1.5*IQR`.

---

### `src/utils/data_profiler.py` — O profiler

Orquestra as duas funções do `analysis_tool` e adiciona preview dos primeiros 5 registros.
O resultado é o `profile` que vai para o `analyze_node` — é esse dicionário que o Claude
recebe para gerar a análise.

---

### `src/report/charts.py` — Gráficos

Gera automaticamente:
- **Scatter matrix** para ver relações entre variáveis numéricas (até 5 colunas)
- **Histograma** para ver a distribuição de cada coluna numérica (até 3 colunas)
- **Boxplot** para visualizar mediana, quartis e outliers de cada coluna (até 3 colunas)

Retorna uma lista de figuras Plotly que o Streamlit renderiza com `st.plotly_chart()`.

---

### `src/report/generator.py` — Gerador de relatório

Usa Jinja2 para renderizar o template `report_template.md` com os dados do estado.
Jinja2 é a mesma engine de templates usada pelo Flask e Django — você coloca
`{{ variavel }}` no template e ela substitui pelo valor real.

---

### `app.py` — Entry point do Streamlit

O ponto de entrada da aplicação. Quando você roda `streamlit run app.py`:
1. O grafo é compilado uma vez (`build_graph()`)
2. A interface aparece com widget de upload
3. Usuário faz upload → arquivo é salvo em disco → `graph.invoke(...)` é chamado
4. Resultado é exibido: relatório em Markdown + gráficos Plotly

---

### `tests/conftest.py` — Fixtures de teste

As fixtures do pytest são funções que criam dados de teste reutilizáveis.
`sample_csv`, `sample_excel` e `sample_json` criam arquivos temporários
com dados de exemplo para os testes rodarem sem depender de arquivos estáticos no repo.

---

## 7. Como rodar localmente

```bash
# 1. Clone o repositório
git clone https://github.com/flaviadeassisbrasil/agente_analise.git
cd agente_analise

# 2. Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate       # Linux/Mac
# venv\Scripts\activate        # Windows

# 3. Instale as dependências
make install
# ou: pip install -r requirements.txt

# 4. Configure a API key do Claude
cp .env.example .env
# edite o .env e coloque sua ANTHROPIC_API_KEY

# 5. Rode a aplicação
make run
# ou: streamlit run app.py

# 6. Rode os testes
make test
# ou: pytest tests/ -v
```

---

## 8. O que ainda falta implementar

O scaffold está completo — a estrutura, os fluxos e os esqueletos de todos os módulos
estão prontos. O que falta é **preencher os TODOs** nas sprints seguintes:

### Sprint 2 — Integração com Claude (prioridade do Igor)

**`src/agent/nodes.py` — `analyze_node`:**
```python
# substituir o placeholder pelo código real:
from langchain_anthropic import ChatAnthropic
from .prompts import SYSTEM_ANALYSIS, build_analysis_prompt

llm = ChatAnthropic(model="claude-sonnet-4-6")
messages = [
    {"role": "system", "content": SYSTEM_ANALYSIS},
    {"role": "user", "content": build_analysis_prompt(state)},
]
response = llm.invoke(messages)
analysis = response.content
```

**`src/agent/nodes.py` — `chat_node`:**
```python
# similar ao analyze_node, mas usando SYSTEM_CHAT
# e pegando a última mensagem do usuário de state["messages"]
```

**`src/agent/prompts.py` — `build_analysis_prompt`:**
```python
# montar o prompt com os dados do profile formatados de forma legível para o Claude
# incluir: shape, colunas, tipos, top correlações, anomalias detectadas, preview
```

### Sprint 2 — Análise e profiling (prioridade da Flávia)

**`src/tools/excel_tool.py` — tratamento de datas:**
```python
# o TODO de tratar tipos de data e colunas duplicadas em read_all_sheets
```

**`src/tools/pdf_tool.py` — extração de tabelas:**
```python
# implementar page.find_tables() do PyMuPDF para extrair tabelas de PDFs
```

**`src/report/charts.py` — mais tipos de gráfico:**
```python
# heatmap de correlação, gráfico de série temporal (se tiver coluna de data),
# gráfico de barras para colunas categóricas
```

### Sprint 3 — Interface Streamlit (prioridade da Flávia)

**`app.py` — UI completa:**
- Layout em colunas (sidebar para upload, área principal para análise)
- Chat interativo com histórico de mensagens
- Botão para download do relatório
- Spinner e feedback de progresso para cada etapa do pipeline

---

## Resumo das dependências principais

| Biblioteca | Para que serve no projeto |
|---|---|
| `langgraph` | Orquestra o fluxo do agente como um grafo de estados |
| `langchain-anthropic` | Conecta o LangGraph ao Claude via API |
| `anthropic` | SDK oficial da Anthropic (base do langchain-anthropic) |
| `streamlit` | Interface web — upload, chat, gráficos |
| `pandas` | Manipulação de dados tabulares (DataFrames) |
| `PyMuPDF` | Extração de texto de PDFs |
| `python-docx` | Leitura de arquivos Word |
| `plotly` | Gráficos interativos |
| `jinja2` | Template engine para o relatório Markdown |
| `ydata-profiling` | Profiling automático avançado (Sprint 2) |
| `weasyprint` | Exportação do relatório para PDF (Sprint 3) |
| `pytest` | Testes automatizados |
| `ruff` | Linter e formatador de código Python |
