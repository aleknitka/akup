from __future__ import annotations

import typer
from rich.console import Console

from cli.client import get_client
from cli.config import load_config, save_config
from cli.display import print_record

app = typer.Typer(help="Manage organizations")
console = Console()


@app.command("bootstrap")
def bootstrap(
    org_name: str = typer.Argument(..., help="Organization name"),
    email: str = typer.Option(..., help="Manager email"),
    password: str = typer.Option(..., prompt=True, hide_input=True, help="Manager password"),
) -> None:
    """Create the first organization and manager account."""
    client = get_client(require_auth=False)
    resp = client.post(
        "/api/v1/auth/bootstrap",
        json={"org_name": org_name, "email": email, "password": password},
    )
    data = resp.json()
    print_record(data, title="Manager Created")
    console.print("[green]Organization bootstrapped. Run 'akup login' to authenticate.[/green]")


@app.command("info")
def info() -> None:
    """Show current organization info."""
    client = get_client()
    resp = client.get("/api/v1/organizations/me")
    print_record(resp.json(), title="Organization")
