import pandas as pd


def describe_dataframe(df: pd.DataFrame) -> dict:
    """Estatísticas descritivas + missing values + correlações."""
    numeric = df.select_dtypes(include="number")

    return {
        "shape": df.shape,
        "dtypes": df.dtypes.astype(str).to_dict(),
        "missing": df.isnull().sum().to_dict(),
        "missing_pct": (df.isnull().mean() * 100).round(2).to_dict(),
        "descriptive": numeric.describe().to_dict() if not numeric.empty else {},
        "correlations": numeric.corr().to_dict() if not numeric.empty else {},
    }


def detect_anomalies(df: pd.DataFrame) -> dict:
    """Detecta outliers via IQR para cada coluna numérica."""
    numeric = df.select_dtypes(include="number")
    anomalies = {}

    for col in numeric.columns:
        q1 = numeric[col].quantile(0.25)
        q3 = numeric[col].quantile(0.75)
        iqr = q3 - q1
        outlier_mask = (numeric[col] < q1 - 1.5 * iqr) | (numeric[col] > q3 + 1.5 * iqr)
        count = int(outlier_mask.sum())
        if count > 0:
            anomalies[col] = {"outlier_count": count, "pct": round(count / len(df) * 100, 2)}

    return anomalies
