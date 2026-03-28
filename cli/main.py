from __future__ import annotations

import httpx
import typer
from rich.console import Console

from cli.commands import evidence, org, user
from cli.commands.init import init
from cli.config import get_api_url, load_config, save_config

app = typer.Typer(
    name="akup",
    help="AKUP Evidence API - CLI client for managing evidence records",
)

console = Console()

app.command("init")(init)
app.add_typer(org.app, name="org")
app.add_typer(user.app, name="user")
app.add_typer(evidence.app, name="evidence")


@app.command("login")
def login(
    email: str = typer.Option(..., prompt=True, help="Your email"),
    password: str = typer.Option(..., prompt=True, hide_input=True, help="Your password"),
) -> None:
    """Authenticate and store a JWT token."""
    url = get_api_url()
    resp = httpx.post(
        f"{url}/api/v1/auth/login",
        data={"username": email, "password": password},
        timeout=30.0,
    )
    if resp.status_code != 200:
        console.print("[red]Login failed.[/red]")
        raise SystemExit(1)
    token = resp.json()["access_token"]
    config = load_config()
    config["token"] = token
    save_config(config)
    console.print("[green]Logged in successfully. Token saved.[/green]")


if __name__ == "__main__":
    app()
