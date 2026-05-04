from jinja2 import Environment, FileSystemLoader
from pathlib import Path


_TEMPLATE_DIR = Path(__file__).parent / "templates"
_env = Environment(loader=FileSystemLoader(str(_TEMPLATE_DIR)))


def generate_report(state: dict) -> str:
    """Monta o relatório Markdown a partir do estado final do agente."""
    template = _env.get_template("report_template.md")
    return template.render(
        file_type=state.get("file_type", "desconhecido"),
        profile=state.get("profile", {}),
        analysis=state.get("analysis", ""),
        chart_count=len(state.get("charts") or []),
    )
