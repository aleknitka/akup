from __future__ import annotations

import typer

from cli.client import get_client
from cli.display import print_evidence_table, print_record

app = typer.Typer(help="Manage evidence records")


@app.command("add")
def add(
    commit_sha: str = typer.Option(..., help="Git commit SHA (7-40 chars)"),
    repo_url: str = typer.Option(..., help="Repository URL"),
    description: str = typer.Option(..., help="Description of creative work"),
    date: str = typer.Option(..., help="Date of work (YYYY-MM-DD)"),
    user_id: str = typer.Option(..., help="User ID who performed the work"),
) -> None:
    """Add a new evidence record."""
    client = get_client()
    resp = client.post(
        "/api/v1/evidence",
        json={
            "commit_sha": commit_sha,
            "repo_url": repo_url,
            "description": description,
            "evidence_date": date,
            "created_by_user_id": user_id,
        },
    )
    print_record(resp.json(), title="Evidence Created")


@app.command("list")
def list_evidence(
    date_from: str | None = typer.Option(None, help="Filter from date (YYYY-MM-DD)"),
    date_to: str | None = typer.Option(None, help="Filter to date (YYYY-MM-DD)"),
    user_id: str | None = typer.Option(None, help="Filter by user ID"),
    limit: int = typer.Option(50, help="Max records to return"),
) -> None:
    """List evidence records with optional filters."""
    client = get_client()
    params: dict[str, str | int] = {"limit": limit}
    if date_from:
        params["date_from"] = date_from
    if date_to:
        params["date_to"] = date_to
    if user_id:
        params["user_id"] = user_id
    resp = client.get("/api/v1/evidence", params=params)
    records = resp.json()
    if not records:
        typer.echo("No evidence records found.")
        return
    print_evidence_table(records)


@app.command("show")
def show(evidence_id: str = typer.Argument(..., help="Evidence record ID")) -> None:
    """Show details of a single evidence record."""
    client = get_client()
    resp = client.get(f"/api/v1/evidence/{evidence_id}")
    print_record(resp.json())


@app.command("generate-description")
def generate_description(
    evidence_id: str = typer.Argument(..., help="Evidence record ID"),
) -> None:
    """Trigger AI description generation for an evidence record."""
    client = get_client()
    resp = client.post(f"/api/v1/evidence/{evidence_id}/generate-description")
    data = resp.json()
    typer.echo(f"AI Description: {data['ai_description']}")
