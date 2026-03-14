from __future__ import annotations

import typer

from cli.commands import evidence, org, user
from cli.commands.init import init

app = typer.Typer(
    name="akup",
    help="AKUP Evidence API - CLI client for managing evidence records",
)

app.command("init")(init)
app.add_typer(org.app, name="org")
app.add_typer(user.app, name="user")
app.add_typer(evidence.app, name="evidence")

if __name__ == "__main__":
    app()
