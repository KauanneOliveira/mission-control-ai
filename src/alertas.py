"""
logica de alertas e decisao automatica do EnviroSat
"""

THRESHOLD_TERMICO_ALERTA    = 50.0   # °C — possivel foco de incendio
THRESHOLD_TERMICO_CRITICO   = 70.0   # °C — foco confirmado / emergencia
THRESHOLD_OPTICO_MIN        = 80.0   # % — abaixo = sensor degradado
THRESHOLD_OPTICO_CRITICO    = 60.0   # % — abaixo = sensor inoperante
THRESHOLD_BUFFER_ALERTA     = 50     # imgs — gargalo de downlink
THRESHOLD_BUFFER_CRITICO    = 100    # imgs — saturacao total
THRESHOLD_GEO_ALERTA        = 10.0   # m — imprecisao de localizacao
THRESHOLD_GEO_CRITICO       = 20.0   # m — geolocalizacao nao confiavel
THRESHOLD_ENERGIA_ALERTA    = 40.0   # % — risco energetico
THRESHOLD_ENERGIA_CRITICO   = 20.0   # % — modo emergencia automatico


def avaliar(dados: dict) -> dict:
    # avalia os dados de telemetria e retorna um dicionário com: alertas, severidade e acoes automaticas
    alertas = []
    acoes_automaticas = []
    nivel_max = "NORMAL"

    termico = dados.get("sensor_termico", 0)

    if termico >= THRESHOLD_TERMICO_CRITICO:
        alertas.append(
            f"🔥 CRÍTICO: Sensor térmico em {termico}°C — foco de incêndio ou queimada ativa provável. "
            f"Área de risco: monitoramento ambiental comprometido se não tratado."
        )
        acoes_automaticas.append("Prioridade de downlink alterada: imagens térmicas desta passagem sobem para URGENTE.")
        acoes_automaticas.append("Notificação automática disparada para coordenador de brigada ambiental.")
        nivel_max = "CRITICO"

    elif termico >= THRESHOLD_TERMICO_ALERTA:
        alertas.append(
            f"⚠️ ALERTA: Sensor térmico em {termico}°C — temperatura acima do normal. "
            f"Possível foco de calor em área monitorada. Verificar imagens ópticas correspondentes."
        )
        nivel_max = _elevar_nivel(nivel_max, "ALERTA")

    optico = dados.get("sensor_optico", 100)

    if optico < THRESHOLD_OPTICO_CRITICO:
        alertas.append(
            f"📷  CRÍTICO: Sensor óptico em {optico}% — sensor praticamente inoperante. "
            f"Imagens RGB+NIR comprometidas. Monitoramento de desmatamento suspenso até reparo."
        )
        acoes_automaticas.append("Modo sensor óptico: STANDBY — economia de energia ativada no payload óptico.")
        nivel_max = "CRITICO"

    elif optico < THRESHOLD_OPTICO_MIN:
        alertas.append(
            f"📷  ALERTA: Sensor óptico em {optico}% — degradação detectada. "
            f"Qualidade de imagem reduzida. Possível interferência por partículas ou microdano."
        )
        nivel_max = _elevar_nivel(nivel_max, "ALERTA")

    buffer = dados.get("buffer_imagens", 0)

    if buffer >= THRESHOLD_BUFFER_CRITICO:
        alertas.append(
            f"💾  CRÍTICO: Buffer de imagens com {buffer} imagens não transmitidas — saturação total. "
            f"Novas capturas serão descartadas até conclusão do downlink."
        )
        acoes_automaticas.append("Captura de novas imagens PAUSADA até buffer abaixo de 50 unidades.")
        nivel_max = "CRITICO"

    elif buffer >= THRESHOLD_BUFFER_ALERTA:
        alertas.append(
            f"💾  ALERTA: Buffer de imagens com {buffer} imagens pendentes — gargalo de downlink. "
            f"Próxima janela de comunicação deve priorizar transmissão."
        )
        nivel_max = _elevar_nivel(nivel_max, "ALERTA")

    geo = dados.get("geolocalizacao", 0)

    if geo >= THRESHOLD_GEO_CRITICO:
        alertas.append(
            f"📍  CRÍTICO: Erro de geolocalização em {geo}m — localização não confiável. "
            f"Coordenadas de focos de incêndio ou desmatamento imprecisas para ação em campo."
        )
        acoes_automaticas.append("Metadados de geolocalização marcados como NÃO CONFIÁVEL nas imagens transmitidas.")
        nivel_max = "CRITICO"

    elif geo >= THRESHOLD_GEO_ALERTA:
        alertas.append(
            f"📍  ALERTA: Erro de geolocalização em {geo}m — precisão abaixo do esperado. "
            f"Verificar sincronização com constelação GNSS de referência."
        )
        nivel_max = _elevar_nivel(nivel_max, "ALERTA")

    energia = dados.get("energia", 100)

    if energia < THRESHOLD_ENERGIA_CRITICO:
        alertas.append(
            f"⚡ CRÍTICO: Energia em {energia}% — nível de emergência. "
            f"Risco de desligamento de sistemas não essenciais."
        )
        acoes_automaticas.append("MODO ECONOMIA DE ENERGIA ATIVADO: sensores secundários desligados.")
        acoes_automaticas.append("Frequência de transmissão reduzida para preservar bateria.")
        nivel_max = "CRITICO"

    elif energia < THRESHOLD_ENERGIA_ALERTA:
        alertas.append(
            f"⚡ ALERTA: Energia em {energia}% — nível abaixo do recomendado. "
            f"Verificar orientação dos painéis solares e consumo dos payloads."
        )
        nivel_max = _elevar_nivel(nivel_max, "ALERTA")

    if not alertas:
        alertas.append("✅ Todos os parâmetros dentro dos ranges normais de operação.")

    return {
        "alertas": alertas,
        "severidade": nivel_max,
        "acoes_automaticas": acoes_automaticas,
    }


def formatar_para_prompt(resultado_alertas: dict) -> str:
    # formata os alertas em texto para exibir no prompt da IA
    linhas = [f"SEVERIDADE ATUAL: {resultado_alertas['severidade']}", "", "ALERTAS DETECTADOS:"]

    for alerta in resultado_alertas["alertas"]:
        linhas.append(f"  - {alerta}")

    if resultado_alertas["acoes_automaticas"]:
        linhas.append("")
        linhas.append("AÇÕES AUTOMÁTICAS JÁ EXECUTADAS PELO SISTEMA:")
        for acao in resultado_alertas["acoes_automaticas"]:
            linhas.append(f"  → {acao}")

    return "\n".join(linhas)


def _elevar_nivel(atual: str, novo: str) -> str:
    # garante que o nível só sobe, nunca desce
    ordem = {"NORMAL": 0, "ALERTA": 1, "CRITICO": 2}
    return novo if ordem.get(novo, 0) > ordem.get(atual, 0) else atual