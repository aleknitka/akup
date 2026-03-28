from __future__ import annotations

import typer
from rich.console import Console

from cli.config import load_config, save_config

console = Console()


def init() -> None:
    """Configure the AKUP CLI with API URL."""
    existing = load_config()

    api_url = typer.prompt(
        "API base URL",
        default=existing.get("api_url", "http://localhost:8000"),
    )

    save_config({"api_url": api_url.rstrip("/")})
    console.print("[green]Configuration saved to ~/.akup/config.json[/green]")
    console.print("Run [bold]akup login[/bold] to authenticate.")
