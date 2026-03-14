from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def truncate(text: str, length: int = 50) -> str:
    if len(text) <= length:
        return text
    return text[: length - 3] + "..."


def print_evidence_table(records: list[dict[str, object]]) -> None:
    table = Table(title="Evidence Records")
    table.add_column("ID", style="dim", max_width=8)
    table.add_column("Date")
    table.add_column("Commit SHA", max_width=10)
    table.add_column("Repo URL", max_width=35)
    table.add_column("Description", max_width=40)
    table.add_column("AI", style="green")

    for r in records:
        table.add_row(
            str(r["id"])[:8],
            str(r["evidence_date"]),
            str(r["commit_sha"])[:10],
            truncate(str(r["repo_url"]), 35),
            truncate(str(r["description"]), 40),
            "Yes" if r.get("ai_description") else "No",
        )
    console.print(table)


def print_users_table(users: list[dict[str, object]]) -> None:
    table = Table(title="Users")
    table.add_column("ID", style="dim", max_width=8)
    table.add_column("Name")
    table.add_column("Email")
    table.add_column("Created")

    for u in users:
        table.add_row(
            str(u["id"])[:8],
            str(u["name"]),
            str(u["email"]),
            str(u["created_at"])[:10],
        )
    console.print(table)


def print_record(record: dict[str, object], title: str = "Evidence Record") -> None:
    lines: list[str] = []
    for key, value in record.items():
        val_str = str(value) if value is not None else "[dim]—[/dim]"
        lines.append(f"[bold]{key}:[/bold] {val_str}")
    console.print(Panel("\n".join(lines), title=title))
