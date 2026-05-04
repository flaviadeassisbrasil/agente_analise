import pandas as pd

from .base import BaseTool


class CSVTool(BaseTool):
    """Lê arquivos CSV com detecção automática de separador e encoding."""

    _SEPARATORS = [",", ";", "\t", "|"]
    _ENCODINGS = ["utf-8", "latin-1", "cp1252"]

    def read(self, file_path: str) -> pd.DataFrame:
        path = self._validate_path(file_path)

        for encoding in self._ENCODINGS:
            for sep in self._SEPARATORS:
                try:
                    df = pd.read_csv(path, sep=sep, encoding=encoding)
                    if df.shape[1] > 1:  # separador correto produz mais de 1 coluna
                        return df
                except Exception:
                    continue

        # fallback: pandas infere o separador
        return pd.read_csv(path)
