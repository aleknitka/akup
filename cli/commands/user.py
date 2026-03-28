from __future__ import annotations

import typer

from cli.client import get_client
from cli.display import print_record, print_users_table

app = typer.Typer(help="Manage users")


@app.command("create")
def create(
    email: str = typer.Argument(..., help="User's email address"),
    password: str = typer.Option(..., prompt=True, hide_input=True, help="Password"),
    role: str = typer.Option("user", help="Role: manager, user, or reporter"),
) -> None:
    """Create a new user in your organization. Display name is auto-assigned."""
    client = get_client()
    resp = client.post(
        "/api/v1/users", json={"email": email, "password": password, "role": role}
    )
    print_record(resp.json(), title="User Created")


@app.command("list")
def list_users() -> None:
    """List all users in your organization."""
    client = get_client()
    resp = client.get("/api/v1/users")
    print_users_table(resp.json())


@app.command("me")
def me() -> None:
    """Show your own profile."""
    client = get_client()
    resp = client.get("/api/v1/users/me")
    print_record(resp.json(), title="My Profile")
