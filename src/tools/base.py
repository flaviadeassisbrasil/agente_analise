from abc import ABC, abstractmethod
from pathlib import Path


class BaseTool(ABC):
    """Interface comum para todas as tools de leitura de arquivo."""

    @abstractmethod
    def read(self, file_path: str):
        """Lê o arquivo e retorna os dados parseados."""
        ...

    def _validate_path(self, file_path: str) -> Path:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        if not path.is_file():
            raise ValueError(f"Caminho não é um arquivo: {file_path}")
        return path
