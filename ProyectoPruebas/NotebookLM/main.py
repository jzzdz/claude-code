#!/usr/bin/env python3
"""
Research Agent — conecta Claude Code con NotebookLM.

Uso:
    python3 main.py "inteligencia artificial en medicina"
    python3 main.py "machine learning" --videos 5 --title "ML Research"
    python3 main.py "blockchain" --videos 8 --exclude 3,5
"""

import asyncio
import webbrowser
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from youtube_search import search_youtube, Video
from notebooklm import upload_videos_to_notebooklm

console = Console()


def display_videos(videos: list[Video]) -> None:
    table = Table(title="Videos encontrados", show_lines=True)
    table.add_column("#", style="dim", width=3)
    table.add_column("Título", style="bold")
    table.add_column("Canal", style="cyan")
    table.add_column("Duración", style="green", justify="right")
    table.add_column("Vistas", style="yellow", justify="right")

    for i, v in enumerate(videos, 1):
        views = f"{v.view_count:,}" if v.view_count else "—"
        table.add_row(str(i), v.title[:60], v.channel[:30], v.duration_fmt(), views)

    console.print(table)


@click.command()
@click.argument("topic")
@click.option("--videos", "-n", default=8, show_default=True, help="Número de videos a buscar")
@click.option("--title", "-t", default=None, help="Título del notebook en NotebookLM")
@click.option("--exclude", "-e", default=None, help="Números de videos a excluir, separados por coma (ej: 2,5)")
@click.option("--dry-run", is_flag=True, help="Solo busca y muestra los videos, sin abrir NotebookLM")
def research(topic: str, videos: int, title: str, exclude: str, dry_run: bool) -> None:
    """Busca videos de YouTube sobre TOPIC y los sube a NotebookLM."""

    notebook_title = title or f"Investigación: {topic}"

    console.print(Panel(
        f"[bold cyan]Research Agent[/bold cyan]\n"
        f"Tema: [bold]{topic}[/bold]\n"
        f"Videos: {videos}  |  Notebook: {notebook_title}",
        expand=False,
    ))

    # 1. Buscar en YouTube
    console.print(f"\n[cyan]Buscando en YouTube:[/cyan] {topic}")
    try:
        results = search_youtube(topic, max_results=videos)
    except RuntimeError as e:
        console.print(f"[red]Error en búsqueda:[/red] {e}")
        raise SystemExit(1)

    if not results:
        console.print("[red]No se encontraron videos.[/red]")
        raise SystemExit(1)

    display_videos(results)

    # 2. Aplicar exclusiones si las hay
    excluded = set()
    if exclude:
        excluded = {int(x.strip()) for x in exclude.split(",") if x.strip().isdigit()}
        if excluded:
            console.print(f"[dim]Excluyendo videos: {sorted(excluded)}[/dim]")

    selected = [v for i, v in enumerate(results, 1) if i not in excluded]

    if not selected:
        console.print("[yellow]Sin videos seleccionados.[/yellow]")
        raise SystemExit(0)

    console.print(f"[green]{len(selected)} videos seleccionados.[/green]\n")

    if dry_run:
        console.print("[yellow]--dry-run activo: no se abrirá NotebookLM.[/yellow]")
        for v in selected:
            console.print(f"  [dim]{v.url}[/dim]")
        return

    # 3. Subir a NotebookLM
    urls = [v.url for v in selected]
    notebook_url = asyncio.run(upload_videos_to_notebooklm(urls, notebook_title))

    # 4. Abrir en el browser real del usuario
    if notebook_url:
        console.print(f"\n[bold green]Abriendo notebook en tu browser:[/bold green] {notebook_url}")
        webbrowser.open(notebook_url)


if __name__ == "__main__":
    research()
