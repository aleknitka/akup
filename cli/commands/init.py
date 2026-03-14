from __future__ import annotations

import typer
from rich.console import Console

from cli.config import load_config, save_config

console = Console()


def init() -> None:
    """Configure the AKUP CLI with API URL and API key."""
    existing = load_config()

    api_url = typer.prompt(
        "API base URL",
        default=existing.get("api_url", "http://localhost:8000"),
    )
    api_key = typer.prompt(
        "API key",
        default=existing.get("api_key", ""),
    )

    save_config({"api_url": api_url.rstrip("/"), "api_key": api_key})
    console.print("[green]Configuration saved to ~/.akup/config.json[/green]")
