import pandas as pd

from .base import BaseTool


class ExcelTool(BaseTool):
    """Lê arquivos XLSX/XLS, suportando múltiplas abas."""

    def read(self, file_path: str) -> pd.DataFrame:
        """Retorna a primeira aba. Use read_all_sheets para todas."""
        path = self._validate_path(file_path)
        return pd.read_excel(path, engine="openpyxl")

    def read_all_sheets(self, file_path: str) -> dict[str, pd.DataFrame]:
        """Retorna dict {nome_aba: DataFrame} para todas as abas."""
        path = self._validate_path(file_path)
        # TODO: tratar tipos de data e colunas com nomes duplicados
        return pd.read_excel(path, sheet_name=None, engine="openpyxl")
