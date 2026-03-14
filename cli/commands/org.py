from __future__ import annotations

import typer
from rich.console import Console

from cli.client import get_client
from cli.config import load_config, save_config
from cli.display import print_record

app = typer.Typer(help="Manage organizations")
console = Console()


@app.command("create")
def create(name: str = typer.Argument(..., help="Organization name")) -> None:
    """Create a new organization and get an API key."""
    client = get_client(require_auth=False)
    resp = client.post("/api/v1/organizations", json={"name": name})
    data = resp.json()
    print_record(data, title="Organization Created")

    if typer.confirm("Save this API key to your config?", default=True):
        config = load_config()
        config["api_key"] = data["api_key"]
        save_config(config)
        console.print("[green]API key saved to config.[/green]")
