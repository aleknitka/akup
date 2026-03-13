from __future__ import annotations

import typer

from cli.client import get_client
from cli.display import print_record, print_users_table

app = typer.Typer(help="Manage users")


@app.command("create")
def create(
    name: str = typer.Argument(..., help="User's full name"),
    email: str = typer.Argument(..., help="User's email address"),
) -> None:
    """Create a new user in your organization."""
    client = get_client()
    resp = client.post("/api/v1/users", json={"name": name, "email": email})
    print_record(resp.json(), title="User Created")


@app.command("list")
def list_users() -> None:
    """List all users in your organization."""
    client = get_client()
    resp = client.get("/api/v1/users")
    print_users_table(resp.json())
