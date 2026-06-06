'''
simula os dados do satelite EnviroSat, gerando os valores de cada sensor a cada leitura
'''

import random
from datetime import datetime

RANGES_NORMAIS = {
    "sensor_termico":   (15.0, 45.0),    # °C — acima indica possível foco de calor incomum
    "sensor_optico":    (85.0, 100.0),   # % — abaixo indica degradação do sensor
    "buffer_imagens":   (0, 50),         # unidades — acima indica gargalo de downlink
    "geolocalizacao":   (1.0, 10.0),     # metros — acima indica imprecisão crítica
    "energia":          (40.0, 100.0),   # % — abaixo indica risco de modo economia
}


def coletar() -> dict:

    cenario_critico = random.random() < 0.10  # 10% de chance

    if cenario_critico:
        dados = _gerar_cenario_critico()
    else:
        dados = _gerar_cenario_normal()

    dados["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dados["ciclo_orbital"] = random.randint(1000, 9999)  # número do ciclo orbital simulado

    return dados


def _gerar_cenario_normal() -> dict:

    return {
        "sensor_termico":   round(random.uniform(15.0, 42.0), 1),
        "sensor_optico":    round(random.uniform(88.0, 100.0), 1),
        "buffer_imagens":   random.randint(0, 40),
        "geolocalizacao":   round(random.uniform(1.0, 8.0), 2),
        "energia":          round(random.uniform(55.0, 100.0), 1),
        "status_geral":     "NOMINAL",
    }


def _gerar_cenario_critico() -> dict:

    tipo = random.choice(["foco_calor", "falha_sensor", "baixa_energia", "gargalo_downlink"])

    base = _gerar_cenario_normal()

    if tipo == "foco_calor":
        base["sensor_termico"] = round(random.uniform(65.0, 95.0), 1)
        base["status_geral"] = "ALERTA — FOCO DE CALOR DETECTADO"

    elif tipo == "falha_sensor":
        base["sensor_optico"] = round(random.uniform(30.0, 70.0), 1)
        base["status_geral"] = "ALERTA — DEGRADAÇÃO DO SENSOR ÓPTICO"

    elif tipo == "baixa_energia":
        base["energia"] = round(random.uniform(10.0, 35.0), 1)
        base["status_geral"] = "ALERTA — ENERGIA CRÍTICA"

    elif tipo == "gargalo_downlink":
        base["buffer_imagens"] = random.randint(80, 150)
        base["status_geral"] = "ALERTA — BUFFER DE IMAGENS SATURADO"

    return base


def formatar_para_prompt(dados: dict) -> str:

    return f"""
=== TELEMETRIA ENVIROSAT — LEITURA ATUAL ===
Timestamp       : {dados.get('timestamp', 'N/A')}
Ciclo Orbital   : #{dados.get('ciclo_orbital', 'N/A')}
Status Geral    : {dados.get('status_geral', 'N/A')}

PARÂMETROS:
  Sensor Térmico (°C)         : {dados.get('sensor_termico', 'N/A')} °C    [normal: 15–45°C]
  Sensor Óptico RGB+NIR (%)   : {dados.get('sensor_optico', 'N/A')}%       [normal: ≥85%]
  Buffer de Imagens (un.)     : {dados.get('buffer_imagens', 'N/A')} imgs  [normal: ≤50]
  Precisão Geolocalização (m) : {dados.get('geolocalizacao', 'N/A')} m     [normal: ≤10m]
  Energia Disponível (%)      : {dados.get('energia', 'N/A')}%             [normal: ≥40%]
============================================
""".strip()