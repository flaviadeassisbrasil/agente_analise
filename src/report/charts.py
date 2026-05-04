import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def generate_charts(df: pd.DataFrame, profile: dict) -> list:
    """Gera lista de figuras Plotly com base no perfil do dataset."""
    charts = []
    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    if len(numeric_cols) >= 2:
        fig = px.scatter_matrix(df[numeric_cols[:5]], title="Matriz de Dispersão")
        charts.append(fig)

    for col in numeric_cols[:3]:
        fig = px.histogram(df, x=col, title=f"Distribuição — {col}")
        charts.append(fig)

        fig = px.box(df, y=col, title=f"Boxplot — {col}")
        charts.append(fig)

    # TODO: adicionar heatmap de correlação, gráficos de série temporal etc.
    return charts
