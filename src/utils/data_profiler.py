import pandas as pd

from ..tools.analysis_tool import describe_dataframe, detect_anomalies


def profile_dataframe(df: pd.DataFrame) -> dict:
    """Monta perfil completo do DataFrame para alimentar o Claude."""
    stats = describe_dataframe(df)
    anomalies = detect_anomalies(df)

    return {
        **stats,
        "anomalies": anomalies,
        "preview": df.head(5).to_dict(orient="records"),
        "columns": list(df.columns),
        "row_count": len(df),
        "column_count": len(df.columns),
    }
