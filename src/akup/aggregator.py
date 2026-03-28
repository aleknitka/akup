"""End-of-day aggregation: scan repos, produce daily summary, commit to evidence repo."""
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import yaml

from akup.config import load_global_config, repo_evidence_dir
from akup.models import EvidenceRecord


def collect_daily_evidence(
    repos: list[Path], target_date: date | None = None
) -> list[EvidenceRecord]:
    """Collect all evidence records from the given repos for a specific date."""
    target = target_date or date.today()
    records: list[EvidenceRecord] = []

    for repo in repos:
        evidence_dir = repo_evidence_dir(repo)
        if not evidence_dir.exists():
            continue
        for path in sorted(evidence_dir.glob("*.yaml")):
            if path.name == "config.yaml":
                continue
            try:
                record = EvidenceRecord.from_file(path)
                record_date = datetime.fromisoformat(record.created_at).date()
                if record_date == target:
                    records.append(record)
            except Exception:
                continue

    return records


def build_daily_report(records: list[EvidenceRecord], target_date: date | None = None) -> dict:
    """Build a structured daily report from evidence records."""
    target = target_date or date.today()
    return {
        "date": target.isoformat(),
        "generated_at": datetime.utcnow().isoformat(timespec="seconds"),
        "total_records": len(records),
        "records": [r.to_dict() for r in records],
    }


def save_daily_report(report: dict, evidence_repo: Path) -> Path:
    """Save a daily report to the evidence repo."""
    reports_dir = evidence_repo / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{report['date']}.yaml"
    path = reports_dir / filename
    path.write_text(yaml.dump(report, default_flow_style=False, sort_keys=False))
    return path


def aggregate(target_date: date | None = None) -> dict:
    """Full aggregation pipeline: collect from all configured repos, build and save report."""
    config = load_global_config()

    repo_paths = [Path(r) for r in config.get("repos", [])]
    evidence_repo = config.get("evidence_repo")

    records = collect_daily_evidence(repo_paths, target_date)
    report = build_daily_report(records, target_date)

    if evidence_repo:
        save_daily_report(report, Path(evidence_repo))

    return report
