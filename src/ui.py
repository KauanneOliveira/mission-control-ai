"""
mostra o banner no inicio, a tabela de comandos, renderiza a resposta da IA num painel bonito e tem o loop principal — fica aqui ate o usuario digitar /exit
"""

from datetime import datetime

import pyfiglet
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style

console = Console()

# Sessão de input com histórico (setas ↑↓ funcionam)
session = PromptSession(
    style=Style.from_dict({"prompt": "#22C55E bold"})
)

COMANDOS = {
    "/help":   "Exibe esta tabela de comandos",
    "/status": "Coleta telemetria e exibe snapshot completo da missão",
    "/about":  "Informações sobre o projeto e a equipe",
    "/clear":  "Limpa o terminal e reexibe o banner",
    "/exit":   "Encerra o Mission Control AI",
}


def _show_banner():
    """Exibe banner ASCII + card de boas-vindas."""
    banner1 = pyfiglet.figlet_format("EnviroSat", font="ansi_shadow")
    banner2 = pyfiglet.figlet_format("Mission Control", font="slant")

    console.print(Align.center(Text(banner1, style="bold #22C55E")))
    console.print(Align.center(Text(banner2, style="bold #06B6D4")))
    console.print(Align.center(
        Text("── 2026.1 · Prompt Engineering and AI · FIAP ──", style="italic #8484A0")
    ))
    console.print()

    console.print(Panel.fit(
        "[bold #22C55E]Trilha:[/bold #22C55E] EnviroSat — Observação Ambiental\n"
        "[bold #06B6D4]Modelo:[/bold #06B6D4] gpt-oss:120b via Ollama Cloud\n"
        "[bold]Agente:[/bold]  GAIA — Geoambiental Artificial Intelligence Agent\n\n"
        "Digite sua pergunta ou use [bold cyan]/help[/bold cyan] para ver os comandos.\n"
        "[dim]Ex: 'Como está a missão?' · 'Há algum foco de incêndio?' · '/status'[/dim]",
        title="◆ MISSION CONTROL AI",
        border_style="#22C55E",
    ))
    console.print()


def _show_help():
    """Exibe tabela de comandos disponíveis."""
    table = Table(title="Comandos disponíveis", border_style="#22C55E", title_style="bold #22C55E")
    table.add_column("Comando", style="bold cyan", no_wrap=True)
    table.add_column("Descrição", style="white")

    for cmd, desc in COMANDOS.items():
        table.add_row(cmd, desc)

    console.print(table)
    console.print()


def _show_response(texto: str, titulo: str = "◆ GAIA  — Mission Control"):
    """Renderiza resposta da IA em painel com timestamp."""
    agora = datetime.now().strftime("%H:%M:%S")
    console.print(Panel(
        texto,
        title=titulo,
        subtitle=f"[dim]{agora}[/dim]",
        border_style="#06B6D4",
    ))
    console.print()


def _show_about():
    """Exibe informações do projeto."""
    console.print(Panel(
        "[bold]Mission Control AI — EnviroSat[/bold]\n\n"
        "Sistema de monitoramento de satélite de observação ambiental.\n"
        "Monitora focos de calor, desmatamento e integridade de áreas protegidas\n"
        "por meio de telemetria simulada e análise por IA generativa.\n\n"
        "[bold #22C55E]Trilha:[/bold #22C55E] EnviroSat · Observação Ambiental\n"
        "[bold #06B6D4]Stack:[/bold #06B6D4] Python · Ollama Cloud · Rich · prompt-toolkit\n"
        "[bold]Disciplina:[/bold] Prompt Engineering and Artificial Intelligence · FIAP 2026.1",
        title="◆ Sobre o Projeto",
        border_style="#8484A0",
    ))
    console.print()


def run_cli(engine):
    """Loop principal da CLI."""
    _show_banner()

    # Aviso se a engine não está pronta (sem API key)
    if not engine.is_ready():
        console.print(Panel(
            "[yellow]⚠ API Key da Ollama não encontrada.[/yellow]\n\n"
            "Crie o arquivo [bold].env[/bold] na raiz do projeto com:\n"
            "  [bold cyan]OLLAMA_API_KEY=sua_chave_aqui[/bold cyan]\n\n"
            "Acesse [link=https://ollama.com]https://ollama.com[/link] para criar sua conta gratuita e gerar a chave.\n\n"
            "[dim]O sistema funcionará, mas as chamadas à IA retornarão erro até a chave ser configurada.[/dim]",
            title="⚠ Engine Status — SEM API KEY",
            border_style="yellow",
        ))
        console.print()

    while True:
        try:
            user_input = session.prompt("❯ ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Encerrando Mission Control AI...[/dim]\n")
            break

        if not user_input:
            continue

        cmd = user_input.lower()

        if cmd == "/exit":
            console.print("\n[dim]Encerrando Mission Control AI. Até a próxima passagem orbital.[/dim]\n")
            break

        elif cmd == "/help":
            _show_help()

        elif cmd == "/status":
            console.print("[dim]Coletando telemetria...[/dim]")
            snapshot = engine.status_snapshot()
            _show_response(snapshot, titulo="◆ Status da Missão — EnviroSat")

        elif cmd == "/about":
            _show_about()

        elif cmd == "/clear":
            console.clear()
            _show_banner()

        else:
            # Qualquer outra entrada vai para o motor de análise com IA
            console.print("[dim]Consultando GAIA...[/dim]")
            resposta = engine.analyze(user_input)
            _show_response(resposta)