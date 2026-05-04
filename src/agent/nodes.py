from langchain_core.messages import AIMessage

from .state import AgentState
from ..utils.file_handler import detect_file_type
from ..tools.csv_tool import CSVTool
from ..tools.excel_tool import ExcelTool
from ..tools.json_tool import JSONTool
from ..tools.pdf_tool import PDFTool
from ..tools.docx_tool import DOCXTool
from ..utils.data_profiler import profile_dataframe
from ..report.charts import generate_charts
from ..report.generator import generate_report

_READERS = {
    "csv": CSVTool(),
    "excel": ExcelTool(),
    "json": JSONTool(),
    "pdf": PDFTool(),
    "docx": DOCXTool(),
}


def parse_node(state: AgentState) -> AgentState:
    file_path = state["file_path"]
    file_type = detect_file_type(file_path)
    reader = _READERS.get(file_type)
    if reader is None:
        return {**state, "error": f"Formato não suportado: {file_type}"}

    result = reader.read(file_path)

    updates: dict = {"file_type": file_type}
    if file_type in ("csv", "excel", "json"):
        updates["dataframe"] = result
    else:
        updates["raw_text"] = result
    return {**state, **updates}


def profile_node(state: AgentState) -> AgentState:
    profile = profile_dataframe(state["dataframe"])
    return {**state, "profile": profile}


def analyze_node(state: AgentState) -> AgentState:
    # TODO: chamar Claude via langchain_anthropic com o perfil/texto
    # from langchain_anthropic import ChatAnthropic
    # from .prompts import build_analysis_prompt
    # llm = ChatAnthropic(model="claude-sonnet-4-6")
    # prompt = build_analysis_prompt(state)
    # response = llm.invoke(prompt)
    # analysis = response.content
    analysis = "TODO: análise gerada pelo Claude"
    return {**state, "analysis": analysis}


def visualize_node(state: AgentState) -> AgentState:
    charts = generate_charts(state["dataframe"], state.get("profile", {}))
    return {**state, "charts": charts}


def report_node(state: AgentState) -> AgentState:
    report = generate_report(state)
    message = AIMessage(content=report)
    return {**state, "report": report, "messages": [message]}


def chat_node(state: AgentState) -> AgentState:
    # TODO: responder perguntas ad-hoc sobre os dados já carregados
    # Tem acesso a state["dataframe"] / state["raw_text"] / state["profile"]
    response = AIMessage(content="TODO: resposta do chat via Claude")
    return {**state, "messages": [response]}
