"""
junta tudo: le a telemetria, avalia os alertas e manda pra IA
"""

import os
from ollama import Client
from dotenv import load_dotenv
from pathlib import Path

from src import telemetria, alertas

load_dotenv()

# configuracao da Ollama Cloud
TRILHA = "envirosat"

_api_key = os.environ.get("OLLAMA_API_KEY", "")

client = Client(
    host="https://ollama.com",
    headers={"Authorization": f"Bearer {_api_key}"}
)


def llm(prompt: str, system: str = None, max_tokens: int = 800, temperature: float = 0.3) -> str:
    # manda o prompt pra IA e devolve o texto
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        return client.chat(
            model="gpt-oss:120b",
            messages=messages,
            options={"num_predict": max_tokens, "temperature": temperature},
            stream=False,
        )["message"]["content"].strip()
    except Exception as e:
        return f"Erro ao consultar IA: {e}"


def _carregar_system_prompt() -> str:
    # le o system prompt do arquivo md
    path = Path("prompts/system_prompt.md")
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "Você é um analista de missão espacial ambiental chamado GAIA."


class MissionEngine:
    # motor de analise — integra telemetria, alertas e IA

    def __init__(self):
        self.trilha = TRILHA
        self.system_prompt = _carregar_system_prompt()
        self._ultimo_dados: dict = {}
        self._ultimo_resultado_alertas: dict = {}
        self._historico: list = []  # guarda os últimos 3 ciclos orbitais

    def is_ready(self) -> bool:
        return bool(_api_key)

    def status_snapshot(self) -> str:
        # coleta telemetria e monta o resumo completo da missao
        dados = telemetria.coletar()
        resultado = alertas.avaliar(dados)

        self._ultimo_dados = dados
        self._ultimo_resultado_alertas = resultado

        resumo_ciclo = (
            f"Ciclo #{dados.get('ciclo_orbital')} | "
            f"Térmico: {dados.get('sensor_termico')}°C | "
            f"Óptico: {dados.get('sensor_optico')}% | "
            f"Buffer: {dados.get('buffer_imagens')} imgs | "
            f"Energia: {dados.get('energia')}% | "
            f"Severidade: {resultado['severidade']}"
        )
        self._historico.append(resumo_ciclo)
        if len(self._historico) > 3:
            self._historico.pop(0)

        # monta texto de saída
        linhas = [
            telemetria.formatar_para_prompt(dados),
            "",
            alertas.formatar_para_prompt(resultado),
        ]
        return "\n".join(linhas)

    def analyze(self, pergunta_usuario: str) -> str:
        # coleta dados frescos, avalia alertas e manda tudo pra IA responder

        # coletagem de dados
        if self._ultimo_dados:
            dados = self._ultimo_dados
            resultado = self._ultimo_resultado_alertas
        else:
            dados = telemetria.coletar()
            resultado = alertas.avaliar(dados)
            self._ultimo_dados = dados
            self._ultimo_resultado_alertas = resultado

        resumo_ciclo = (
            f"Ciclo #{dados.get('ciclo_orbital')} | "
            f"Térmico: {dados.get('sensor_termico')}°C | "
            f"Óptico: {dados.get('sensor_optico')}% | "
            f"Buffer: {dados.get('buffer_imagens')} imgs | "
            f"Energia: {dados.get('energia')}% | "
            f"Severidade: {resultado['severidade']}"
        )
        self._historico.append(resumo_ciclo)
        if len(self._historico) > 3:
            self._historico.pop(0)

        # monta o historico dos ciclos anteriore
        historico_texto = ""
        if len(self._historico) > 1:
            historico_texto = "\n=== HISTÓRICO DOS ÚLTIMOS CICLOS ORBITAIS ===\n"
            for h in self._historico[:-1]:
                historico_texto += f"  {h}\n"
            historico_texto += "==============================================\n"

        # prompt completo
        telemetria_texto = telemetria.formatar_para_prompt(dados)
        alertas_texto = alertas.formatar_para_prompt(resultado)

        prompt = f"""
        {historico_texto}
        {telemetria_texto}
        
        {alertas_texto}
        
        === PERGUNTA DO OPERADOR ===
        {pergunta_usuario}
        ============================
        
        Responda como GAIA, analista de missão do EnviroSat. Siga a estrutura: diagnóstico técnico → impacto terrestre → recomendação de ação.
        """.strip()

        return llm(prompt, system=self.system_prompt)