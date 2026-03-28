"""CLI interface with JSON output mode for Ink frontend."""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from akup.aggregator import aggregate
from akup.artifacts import resolve_artifact
from akup.config import (
    get_display_name,
    load_global_config,
    load_repo_config,
    save_global_config,
    save_repo_config,
)
from akup.git_ops import find_repo_root
from akup.hooks import install_hook, is_hook_installed, uninstall_hook
from akup.recorder import list_evidence, record_commit, record_manual

app = typer.Typer(name="akup", help="Distributed evidence recording for autorskie koszty")
console = Console()


def _json_mode() -> bool:
    return "--json" in sys.argv


def _output(data: object) -> None:
    if _json_mode():
        typer.echo(json.dumps(data, default=str))
    else:
        console.print_json(json.dumps(data, default=str))


# --- init ---


@app.command()
def init(
    jira_url: str = typer.Option("", help="Jira base URL"),
    jira_project: str = typer.Option("", help="Jira project key"),
    confluence_url: str = typer.Option("", help="Confluence base URL"),
    confluence_space: str = typer.Option("", help="Confluence space key"),
) -> None:
    """Initialize akup in the current git repo."""
    repo = find_repo_root()
    display_name = get_display_name()

    repo_config: dict = {}
    if jira_url:
        repo_config["jira"] = {"url": jira_url, "project": jira_project}
    if confluence_url:
        repo_config["confluence"] = {"url": confluence_url, "space": confluence_space}
    save_repo_config(repo, repo_config)

    # Install git hook
    install_hook(repo)

    # Register this repo in global config
    global_cfg = load_global_config()
    repos = global_cfg.get("repos", [])
    repo_str = str(repo)
    if repo_str not in repos:
        repos.append(repo_str)
        global_cfg["repos"] = repos
        save_global_config(global_cfg)

    if _json_mode():
        _output({
            "repo": repo_str,
            "display_name": display_name,
            "hook_installed": True,
            "config": repo_config,
        })
    else:
        console.print(f"[green]Initialized akup in {repo}[/green]")
        console.print(f"Your display name: [bold]{display_name}[/bold]")
        console.print("[green]Post-commit hook installed.[/green]")


# --- record ---


@app.command()
def record(
    auto: bool = typer.Option(False, help="Auto mode (called by git hook)"),
    description: str = typer.Option("", help="Description of creative work"),
    sha: str = typer.Option("HEAD", help="Commit SHA to record"),
    jira: str = typer.Option("", help="Jira issue ID to link (e.g. PROJ-123)"),
    confluence: str = typer.Option("", help="Confluence page ID to link"),
    json_out: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """Record evidence for a commit."""
    repo = find_repo_root()

    evidence = record_commit(repo, sha=sha, description=description)

    # Attach artifacts
    if jira or confluence:
        repo_config = load_repo_config(repo)
        if jira:
            artifact = resolve_artifact(repo_config, "jira", jira)
            evidence.artifacts.append(artifact)
        if confluence:
            artifact = resolve_artifact(repo_config, "confluence", confluence)
            evidence.artifacts.append(artifact)
        # Re-save with artifacts
        from akup.config import repo_evidence_dir

        evidence.save(repo_evidence_dir(repo))

    if _json_mode() or json_out:
        _output(evidence.to_dict())
    elif not auto:
        console.print(f"[green]Evidence recorded:[/green] {evidence.id[:8]}")
        console.print(f"  Commit: {evidence.commit_sha[:10]}")
        console.print(f"  Files: {evidence.diff_stat.files_changed} changed")
        console.print(f"  Description: {evidence.description}")


# --- list ---


@app.command("list")
def list_cmd(
    date_filter: str = typer.Option("", "--date", help="Filter by date (YYYY-MM-DD)"),
    json_out: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """List evidence records in the current repo."""
    repo = find_repo_root()
    records = list_evidence(repo)

    if date_filter:
        target = date.fromisoformat(date_filter)
        from datetime import datetime

        records = [
            r
            for r in records
            if datetime.fromisoformat(r.created_at).date() == target
        ]

    if _json_mode() or json_out:
        _output([r.to_dict() for r in records])
        return

    if not records:
        console.print("[dim]No evidence records found.[/dim]")
        return

    table = Table(title="Evidence Records")
    table.add_column("ID", style="dim", max_width=8)
    table.add_column("Date")
    table.add_column("SHA", max_width=10)
    table.add_column("Description", max_width=50)
    table.add_column("Files")
    table.add_column("Artifacts")

    for r in records:
        table.add_row(
            r.id[:8],
            r.created_at[:10],
            r.commit_sha[:10] if r.commit_sha else "-",
            r.description[:50],
            str(r.diff_stat.files_changed),
            str(len(r.artifacts)),
        )
    console.print(table)


# --- show ---


@app.command()
def show(
    record_id: str = typer.Argument(..., help="Evidence record ID (prefix match)"),
    json_out: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """Show details of an evidence record."""
    repo = find_repo_root()
    records = list_evidence(repo)

    match = [r for r in records if r.id.startswith(record_id)]
    if not match:
        console.print(f"[red]No record found matching '{record_id}'[/red]")
        raise typer.Exit(1)

    record = match[0]

    if _json_mode() or json_out:
        _output(record.to_dict())
        return

    lines = [
        f"[bold]ID:[/bold] {record.id}",
        f"[bold]Commit:[/bold] {record.commit_sha}",
        f"[bold]Branch:[/bold] {record.branch}",
        f"[bold]Repo:[/bold] {record.repo_url or record.repo_path}",
        f"[bold]Description:[/bold] {record.description}",
        f"[bold]Files changed:[/bold] {record.diff_stat.files_changed} "
        f"(+{record.diff_stat.insertions} -{record.diff_stat.deletions})",
        f"[bold]Author:[/bold] {record.author_display_name}",
        f"[bold]Created:[/bold] {record.created_at}",
    ]
    if record.artifacts:
        lines.append("[bold]Artifacts:[/bold]")
        for a in record.artifacts:
            lines.append(f"  [{a.type}] {a.id} — {a.title or a.url}")
    if record.diff_stat.files:
        lines.append("[bold]Changed files:[/bold]")
        for f in record.diff_stat.files:
            lines.append(f"  {f}")
    console.print(Panel("\n".join(lines), title="Evidence Record"))


# --- hook management ---


@app.command("hook")
def hook_cmd(
    action: str = typer.Argument(..., help="install / uninstall / status"),
) -> None:
    """Manage the post-commit git hook."""
    repo = find_repo_root()

    if action == "install":
        install_hook(repo)
        console.print("[green]Post-commit hook installed.[/green]")
    elif action == "uninstall":
        if uninstall_hook(repo):
            console.print("[yellow]Post-commit hook removed.[/yellow]")
        else:
            console.print("[dim]No akup hook found.[/dim]")
    elif action == "status":
        installed = is_hook_installed(repo)
        if _json_mode():
            _output({"installed": installed})
        else:
            status = "[green]installed[/green]" if installed else "[red]not installed[/red]"
            console.print(f"Post-commit hook: {status}")
    else:
        console.print(f"[red]Unknown action: {action}. Use install/uninstall/status.[/red]")


# --- aggregate ---


@app.command("aggregate")
def aggregate_cmd(
    target_date: str = typer.Option("", "--date", help="Date to aggregate (YYYY-MM-DD)"),
    json_out: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """Aggregate daily evidence from all configured repos."""
    dt = date.fromisoformat(target_date) if target_date else None
    report = aggregate(dt)

    if _json_mode() or json_out:
        _output(report)
        return

    console.print(f"[bold]Daily Report: {report['date']}[/bold]")
    console.print(f"Total records: {report['total_records']}")
    for r in report["records"]:
        sha = r["commit_sha"][:8] if r["commit_sha"] else "manual"
        console.print(f"  [{sha}] {r['description'][:60]}")


# --- config ---


@app.command("config")
def config_cmd(
    json_out: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """Show current configuration."""
    global_cfg = load_global_config()

    try:
        repo = find_repo_root()
        repo_cfg = load_repo_config(repo)
    except RuntimeError:
        repo_cfg = {}

    data = {"global": global_cfg, "repo": repo_cfg}

    if _json_mode() or json_out:
        _output(data)
    else:
        console.print_json(json.dumps(data, default=str))


if __name__ == "__main__":
    app()
