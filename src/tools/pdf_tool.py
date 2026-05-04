import fitz  # PyMuPDF

from .base import BaseTool


class PDFTool(BaseTool):
    """Extrai texto e tabelas de arquivos PDF via PyMuPDF."""

    def read(self, file_path: str) -> str:
        path = self._validate_path(file_path)

        text_blocks = []
        with fitz.open(str(path)) as doc:
            for page in doc:
                text_blocks.append(page.get_text())

        return "\n\n".join(text_blocks)

    # TODO: implementar extração de tabelas com page.find_tables()
