from typing import Annotated, Any, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    # Mensagens do chat (acumuladas via add_messages)
    messages: Annotated[list, add_messages]

    # Arquivo carregado
    file_path: Optional[str]
    file_type: Optional[str]  # "csv" | "excel" | "json" | "pdf" | "docx"

    # Dados parseados — apenas um dos dois é preenchido por run
    dataframe: Optional[Any]   # pd.DataFrame para dados tabulares
    raw_text: Optional[str]    # texto extraído de PDF/DOCX

    # Pipeline de análise
    profile: Optional[dict]    # saída do data_profiler
    analysis: Optional[str]    # análise gerada pelo Claude
    charts: Optional[list]     # lista de figuras Plotly (JSON-serializable)
    report: Optional[str]      # relatório final em Markdown

    # Controle de fluxo
    error: Optional[str]
