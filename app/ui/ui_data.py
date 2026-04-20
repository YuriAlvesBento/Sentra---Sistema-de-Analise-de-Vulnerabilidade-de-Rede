from __future__ import annotations

APP_TITLE = "SENTRA - Sistema Especializado de Analise de Rede e Testes de Auditoria"

TAB_PATHS = {
    "nova_analise": r"SENTRA\Nova Analise",
    "resultados": r"SENTRA\Dispositivos Detectados\Resultados",
    "vulnerabilidades": r"SENTRA\Achados de Seguranca",
    "relatorios": r"SENTRA\Relatorios",
    "configuracoes": r"SENTRA\Configuracoes",
    "logs": r"SENTRA\Logs do Sistema",
    "historico": r"SENTRA\Historico de Scans",
}

RESULT_COLUMNS = [
    ("Host", "host"),
    ("IP", "ip"),
    ("Porta", "port"),
    ("Proto", "protocol"),
    ("Servico", "service"),
    ("Versao", "version"),
    ("Sistema", "os"),
    ("Status", "status"),
    ("Risco", "risk"),
    ("Referencia", "reference"),
]

RESULT_ROWS = []

FINDING_COLUMNS = [
    ("Severidade", "severity"),
    ("Referencia", "reference"),
    ("Descricao", "description"),
    ("Host", "host"),
    ("Porta / Servico", "service_port"),
    ("CVSS", "cvss"),
    ("Recomendacao", "recommendation"),
]

FINDING_ROWS = []

REPORT_ROWS = []

HISTORY_ROWS = []

BOOT_LOGS = []

SCAN_STEPS = []

DETAIL_DEFAULT = {}

RISK_COLORS = {
    "CRITICO": ("#f8d7da", "#9f1c28"),
    "ALTO": ("#fde2c7", "#9d4d00"),
    "MEDIO": ("#fff3bf", "#7a5d00"),
    "BAIXO": ("#d3f9d8", "#1d6f42"),
}

STATUS_COLORS = {
    "Aberta": "#0f7b0f",
    "Filtrada": "#a46a00",
    "Fechada": "#b02a37",
}
