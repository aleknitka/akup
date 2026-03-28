# AKUP — Distributed Evidence Recorder

CLI tool for recording evidence of creative/authorial work for **AKUP** (autorskie koszty uzyskania przychodu) — the Polish tax regulation allowing 50% income deduction for author's costs.

Evidence is captured automatically from git commits and linked to artifacts (Jira tickets, Confluence pages) to create a verifiable audit trail.

## Architecture

```
Developer's machine
├── Git repos (each with .akup/evidence/*.yaml)
│   ├── post-commit hook → auto-records evidence
│   └── .akup/config.yaml (Jira/Confluence settings)
├── akup CLI (Python)
│   ├── record   — capture evidence from commits
│   ├── list     — browse evidence
│   ├── aggregate — daily report across all repos
│   └── --json   — structured output for Ink TUI
└── ~/.akup/config.yaml (global: repo list, display name)
```

**No server needed.** Evidence lives as YAML files committed alongside your code. Git is the storage layer and audit trail.

## How It Works

1. Run `akup init` in a repo — installs a post-commit hook
2. Every commit automatically creates an evidence record in `.akup/evidence/`
3. Each record captures: commit SHA, diff stats, changed files, branch, description
4. Optionally link Jira tickets and Confluence pages for full traceability
5. At end of day, `akup aggregate` collects evidence from all repos into a daily report

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- Git

## Getting Started

```bash
# Install
uv sync

# Initialize in a git repo
cd /path/to/your/repo
uv run akup init

# Optionally configure Jira/Confluence
uv run akup init \
  --jira-url https://jira.example.com \
  --jira-project PROJ \
  --confluence-url https://wiki.example.com \
  --confluence-space ENG
```

This does three things:
1. Creates `.akup/config.yaml` in the repo
2. Installs a post-commit git hook
3. Registers the repo in your global config (`~/.akup/config.yaml`)

Now every commit will auto-record evidence.

## CLI Commands

### Recording evidence

```bash
# Auto-recorded by git hook on each commit — no action needed

# Manually record with a custom description
uv run akup record --description "Designed auth architecture with PKCE flow"

# Record with linked artifacts
uv run akup record \
  --description "Implemented OAuth2 module" \
  --jira PROJ-123 \
  --confluence 12345678
```

### Browsing evidence

```bash
# List all evidence in current repo
uv run akup list

# Filter by date
uv run akup list --date 2026-03-28

# Show details of a specific record (prefix match on ID)
uv run akup show a1b2c3d4
```

### Daily aggregation

```bash
# Aggregate today's evidence from all configured repos
uv run akup aggregate

# Aggregate a specific date
uv run akup aggregate --date 2026-03-28
```

If `evidence_repo` is set in `~/.akup/config.yaml`, the daily report is saved there as `reports/YYYY-MM-DD.yaml`.

### Hook management

```bash
uv run akup hook install    # Install post-commit hook
uv run akup hook uninstall  # Remove it
uv run akup hook status     # Check if installed
```

### Configuration

```bash
uv run akup config          # Show current config (global + repo)
```

### JSON output

Every command supports `--json` for machine-readable output (used by the Ink TUI frontend):

```bash
uv run akup list --json
uv run akup show a1b2c3d4 --json
uv run akup aggregate --json
```

## Evidence Record Format

Each record is a YAML file in `.akup/evidence/`:

```yaml
version: 1
id: a1b2c3d4-5678-...
commit_sha: abc1234def5678901234567890abcdef12345678
repo_url: https://github.com/org/repo
branch: feature/auth
diff_stat:
  files_changed: 3
  insertions: 47
  deletions: 12
  files:
    - src/auth.py
    - src/models/user.py
    - tests/test_auth.py
description: Implemented OAuth2 authentication with PKCE flow
artifacts:
  - type: jira
    id: PROJ-123
    url: https://jira.example.com/browse/PROJ-123
    title: Implement auth module
    status: In Progress
  - type: confluence
    id: '12345678'
    url: https://wiki.example.com/pages/12345678
    title: Auth Architecture Decision Record
    version: '5'
author_display_name: Brave Falcon
created_at: '2026-03-28T09:15:00'
```

## Audit Trail

The audit trail is verifiable at every level:

| What | How to verify |
|---|---|
| Commit exists | `git log <sha>` in the repo |
| Diff matches | `git diff-tree --stat <sha>` |
| Jira ticket | Follow URL or call Jira API |
| Confluence page | Follow URL or call Confluence API |
| Timestamp | Git commit timestamp of the evidence file itself |
| Author | Display name mapped in `~/.akup/config.yaml` |

Evidence files are committed to the repo, so they have their own git history — tampering is detectable.

## Configuration

### Global (`~/.akup/config.yaml`)

```yaml
display_name: Brave Falcon
repos:
  - /home/user/projects/repo1
  - /home/user/projects/repo2
evidence_repo: /home/user/evidence-archive
```

### Per-repo (`.akup/config.yaml`)

```yaml
jira:
  url: https://jira.example.com
  project: PROJ
  email: user@example.com
  token: your-api-token
confluence:
  url: https://wiki.example.com
  space: ENG
  email: user@example.com
  token: your-api-token
```

## Privacy

- No real names stored — each user gets an auto-assigned display name (e.g. "Brave Falcon", "Quick Otter")
- Jira/Confluence tokens are stored in local config only, never in evidence files
- Evidence files contain only commit metadata and artifact references

## Running Tests

```bash
uv run pytest -v
```

31 tests covering: models, git operations, hooks, recording, aggregation, and configuration.

## Project Structure

```
akup/
├── src/akup/
│   ├── cli.py          # Typer CLI with --json output
│   ├── config.py       # Global + per-repo config, display name generator
│   ├── models.py       # EvidenceRecord dataclass + YAML serialization
│   ├── git_ops.py      # Git operations (commit info, diff stats)
│   ├── hooks.py        # Post-commit hook install/uninstall
│   ├── recorder.py     # Evidence creation (auto + manual)
│   ├── artifacts.py    # Jira + Confluence API clients
│   └── aggregator.py   # Daily report generation across repos
├── tests/              # Pytest test suite
├── pyproject.toml      # Dependencies and tool config
└── uv.lock
```

## License

See [LICENSE](LICENSE).
