# Relatório DataLens

**Formato:** {{ file_type | upper }}
**Linhas:** {{ profile.get('row_count', '—') }}
**Colunas:** {{ profile.get('column_count', '—') }}
**Gráficos gerados:** {{ chart_count }}

---

## Análise

{{ analysis }}

---

## Perfil Estatístico

{% if profile.descriptive %}
### Estatísticas Descritivas
{% for col, stats in profile.descriptive.items() %}
**{{ col }}**
- Média: {{ "%.2f"|format(stats.get('mean', 0)) }}
- Desvio Padrão: {{ "%.2f"|format(stats.get('std', 0)) }}
- Mín: {{ "%.2f"|format(stats.get('min', 0)) }} | Máx: {{ "%.2f"|format(stats.get('max', 0)) }}
{% endfor %}
{% endif %}

{% if profile.anomalies %}
### Anomalias Detectadas
{% for col, info in profile.anomalies.items() %}
- **{{ col }}**: {{ info.outlier_count }} outliers ({{ info.pct }}%)
{% endfor %}
{% endif %}

{% if profile.missing %}
### Valores Ausentes
{% for col, count in profile.missing.items() %}{% if count > 0 %}
- **{{ col }}**: {{ count }} ({{ profile.missing_pct[col] }}%)
{% endif %}{% endfor %}
{% endif %}

---
*Gerado pelo DataLens Agent*
