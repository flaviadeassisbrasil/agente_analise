from langgraph.graph import StateGraph, START, END

from .state import AgentState
from .nodes import parse_node, profile_node, analyze_node, visualize_node, report_node, chat_node


def _route_entry(state: AgentState) -> str:
    """Decide o ponto de entrada: novo arquivo → parse | pergunta → chat."""
    has_file = bool(state.get("file_path"))
    already_parsed = state.get("dataframe") is not None or state.get("raw_text") is not None
    if has_file and not already_parsed:
        return "parse"
    return "chat"


def _route_after_parse(state: AgentState) -> str:
    """Dados tabulares → profile | documentos → analyze."""
    if state.get("dataframe") is not None:
        return "profile"
    return "analyze"


def _route_after_analyze(state: AgentState) -> str:
    """Dados tabulares → visualize | documentos → report."""
    if state.get("dataframe") is not None:
        return "visualize"
    return "report"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("parse", parse_node)
    graph.add_node("profile", profile_node)
    graph.add_node("analyze", analyze_node)
    graph.add_node("visualize", visualize_node)
    graph.add_node("report", report_node)
    graph.add_node("chat", chat_node)

    graph.add_conditional_edges(START, _route_entry, {"parse": "parse", "chat": "chat"})

    graph.add_conditional_edges("parse", _route_after_parse, {"profile": "profile", "analyze": "analyze"})

    graph.add_edge("profile", "analyze")

    graph.add_conditional_edges("analyze", _route_after_analyze, {"visualize": "visualize", "report": "report"})

    graph.add_edge("visualize", "report")
    graph.add_edge("report", END)
    graph.add_edge("chat", END)

    return graph.compile()
