"""
gerador de banner ASCII para o Mission Control AI EnviroSat
"""

import sys
import pyfiglet
from rich.console import Console
from rich.align import Align
from rich.text import Text

console = Console()


def mostrar_banner(font="ansi_shadow"):
    linha1 = pyfiglet.figlet_format("EnviroSat", font=font)
    linha2 = pyfiglet.figlet_format("Mission Control", font=font)

    console.print(Align.center(Text(linha1, style="bold #22C55E ")))   # verde - arvore / mata
    console.print(Align.center(Text(linha2, style="bold #15803D")))
    console.print(Align.center(
        Text("── FIAP GS2026.1 · Prompt Engineering and AI ──",
             style="italic #15803D")
    ))


def listar_fontes():
    # lista todas as fontes disponiveis no pyfiglet
    fontes = pyfiglet.FigletFont.getFonts()
    console.print(f"[bold]Fontes disponíveis ({len(fontes)}):[/bold]")
    for f in sorted(fontes):
        console.print(f"  {f}")


def demo():
    # demonstra 8 fontes diferente
    fontes = ["ansi_shadow", "slant", "big", "banner3", "doom", "standard", "block", "digital"]
    for f in fontes:
        console.rule(f"[bold 15803d]{f}[/bold 15803d]")
        try:
            txt = pyfiglet.figlet_format("EnviroSat", font=f)
            console.print(Text(txt, style="bold #22C55E "))
        except Exception:
            console.print(f"[red]Fonte {f} não disponível[/red]")


if __name__ == "__main__":
    args = sys.argv[1:]

    if "-fonts" in args:
        listar_fontes()
    elif "-demo" in args:
        demo()
    elif "-font" in args:
        idx = args.index("-font")
        font = args[idx + 1] if idx + 1 < len(args) else "ansi_shadow"
        texto = args[args.index("-text") + 1] if "-text" in args else "EnviroSat"
        console.print(Text(pyfiglet.figlet_format(texto, font=font), style="bold #22C55E "))
    else:
        mostrar_banner()