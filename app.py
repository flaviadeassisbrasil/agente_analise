import streamlit as st
from dotenv import load_dotenv

from src.agent import build_graph
from src.utils.file_handler import save_upload

load_dotenv()

st.set_page_config(page_title="DataLens", page_icon="🔍", layout="wide")
st.title("DataLens — Agente de Análise de Dados")

# TODO: Sprint 3 — implementar UI completa
# Por ora o app.py serve como ponto de entrada para validar o grafo

graph = build_graph()

uploaded_file = st.file_uploader(
    "Faça upload do seu arquivo",
    type=["csv", "xlsx", "xls", "json", "pdf", "docx"],
)

if uploaded_file:
    file_path = save_upload(uploaded_file)
    st.success(f"Arquivo salvo: {uploaded_file.name}")

    if st.button("Analisar"):
        with st.spinner("Analisando..."):
            result = graph.invoke({"file_path": file_path, "messages": []})

        if result.get("error"):
            st.error(result["error"])
        else:
            if result.get("report"):
                st.markdown(result["report"])
            for chart in result.get("charts") or []:
                st.plotly_chart(chart, use_container_width=True)

st.divider()
st.caption("DataLens · LangGraph + Claude API · Streamlit")
