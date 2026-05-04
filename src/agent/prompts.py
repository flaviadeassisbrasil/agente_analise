SYSTEM_ANALYSIS = """Você é um analista de dados especialista.
Receberá o perfil estatístico de um dataset e deverá gerar uma análise clara e objetiva,
estruturada em: Visão Geral, Principais Insights, Anomalias Detectadas e Recomendações.
Responda sempre em português. Seja direto e técnico."""

SYSTEM_CHAT = """Você é um assistente de análise de dados.
O usuário já fez upload de um arquivo e você tem acesso ao perfil estatístico completo dos dados.
Responda perguntas sobre os dados de forma clara e precisa, em português."""


def build_analysis_prompt(state: dict) -> str:
    # TODO: montar prompt completo com profile e metadados do dataset
    profile = state.get("profile", {})
    return f"Analise o seguinte perfil de dados:\n\n{profile}"


def build_chat_prompt(state: dict, question: str) -> str:
    # TODO: montar prompt com contexto dos dados e pergunta do usuário
    return f"Com base nos dados carregados, responda: {question}"
