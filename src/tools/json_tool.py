import json
import pandas as pd

from .base import BaseTool


class JSONTool(BaseTool):
    """Lê arquivos JSON e converte para DataFrame, achatando estruturas nested."""

    def read(self, file_path: str) -> pd.DataFrame:
        path = self._validate_path(file_path)

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            return pd.json_normalize(data)

        if isinstance(data, dict):
            # tenta encontrar a lista principal de registros dentro do dict
            for value in data.values():
                if isinstance(value, list):
                    return pd.json_normalize(value)
            # se não há lista, normaliza o dict inteiro como um único registro
            return pd.json_normalize([data])

        raise ValueError(f"Estrutura JSON não suportada: {type(data)}")
