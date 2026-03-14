# AKUP Evidence API

REST API for recording evidence of creative/authorial work for the purpose of **AKUP** (autorskie koszty uzyskania przychodu) — the Polish tax regulation that allows employees to deduct 50% of their income as author's costs when their work involves creative contributions (software development, design, research, etc.).

Businesses use this application to maintain a structured database of evidence records — linking git commits, descriptions of work, and AI-generated summaries — that can be referenced during tax audits.

## Architecture

```
┌─────────────────┐        HTTP / JSON        ┌──────────────────────┐
│   Client         │ ──────────────────────── │   AKUP API Server     │
│                  │                           │   (FastAPI + uvicorn) │
│  - curl          │   X-API-Key header        │                      │
│  - Swagger UI    │ ◄──────────────────────── │   SQLAlchemy (async)  │
│  - custom app    │                           │         │             │
│  - CI pipeline   │                           │         ▼             │
└─────────────────┘                           │   PostgreSQL / SQLite │
                                              └──────────────────────┘
```

The application includes three ways to interact with the API:

- **CLI tool** (`akup`) — a command-line client for developers. Create orgs, users, and evidence records directly from the terminal.
- **Web UI** — a lightweight browser-based interface at `http://localhost:8000/` for browsing and managing evidence records.
- **Swagger UI** — built into FastAPI at `http://localhost:8000/docs` for exploring the raw API interactively.
- **curl / httpx** — direct HTTP calls, examples shown below.

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (Python package manager)

## Getting Started

### 1. Install dependencies

```bash
uv sync
```

This creates a virtual environment in `.venv/` and installs all dependencies.

### 2. Configure the database

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` to set your database URL:

```bash
# Local development (SQLite) — this is the default, no changes needed:
AKUP_DATABASE_URL=sqlite+aiosqlite:///./akup.db

# Production (PostgreSQL on Azure or elsewhere):
AKUP_DATABASE_URL=postgresql+asyncpg://user:password@host:5432/akup
```

### 3. Initialize the database

Run Alembic migrations to create the tables:

```bash
uv run alembic upgrade head
```

This works with both SQLite and PostgreSQL — the migration files are database-agnostic.

### 4. Start the server

```bash
uv run uvicorn app.main:app --reload
```

The API is now available at `http://localhost:8000`. Open `http://localhost:8000/docs` for the interactive Swagger UI.

## CLI Usage

The `akup` CLI is installed automatically with the project. All commands use the config stored in `~/.akup/config.json`.

### Setup

```bash
# Configure API URL (defaults to http://localhost:8000)
uv run akup init

# Or create an org first and save the API key in one step
uv run akup org create "My Company"
```

### Managing users

```bash
uv run akup user create "Jan Kowalski" "jan@example.com"
uv run akup user list
```

### Managing evidence

```bash
# Add a record
uv run akup evidence add \
  --commit-sha a1b2c3d4e5f6 \
  --repo-url https://github.com/org/repo \
  --description "Implemented OAuth2 authentication module" \
  --date 2026-03-13 \
  --user-id <user-id>

# List records (with optional filters)
uv run akup evidence list
uv run akup evidence list --date-from 2026-03-01 --date-to 2026-03-31

# View details
uv run akup evidence show <evidence-id>

# Generate AI description
uv run akup evidence generate-description <evidence-id>
```

### All CLI commands

```
akup init                          Configure API URL and API key
akup org create <name>             Create organization (returns API key)
akup user create <name> <email>    Create user
akup user list                     List users
akup evidence add                  Add evidence record
akup evidence list                 List evidence (with filters)
akup evidence show <id>            Show evidence detail
akup evidence generate-description <id>  Generate AI description
```

## Web UI

Open `http://localhost:8000/` in your browser. The web interface provides:

1. **Login page** — enter your organization's API key
2. **Dashboard** — browse evidence records in a table, filter by date or user
3. **Add Evidence** — form to create new evidence records
4. **Detail view** — view all fields, generate AI descriptions, delete records

The web UI uses Pico CSS for styling and vanilla JavaScript — no build step required.

## API Usage (curl)

Below is a complete workflow using `curl`. Every request (except creating an organization) requires the `X-API-Key` header.

### Step 1: Create an organization

This is the bootstrap step. No authentication required. The response includes the API key you'll use for all subsequent requests.

```bash
curl -s -X POST http://localhost:8000/api/v1/organizations \
  -H "Content-Type: application/json" \
  -d '{"name": "My Company"}' | python -m json.tool
```

Response:
```json
{
    "id": "a1b2c3d4-...",
    "name": "My Company",
    "api_key": "abc123...",
    "created_at": "2026-03-13T10:00:00"
}
```

Save the `api_key` value — you'll need it for everything else:

```bash
export API_KEY="abc123..."
```

### Step 2: Create a user

```bash
curl -s -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"name": "Jan Kowalski", "email": "jan@example.com"}' | python -m json.tool
```

Save the user `id` from the response:

```bash
export USER_ID="e5f6g7h8-..."
```

### Step 3: Record evidence

Create an evidence record linking a git commit to a description of creative work:

```bash
curl -s -X POST http://localhost:8000/api/v1/evidence \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"commit_sha\": \"a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2\",
    \"repo_url\": \"https://github.com/mycompany/myproject\",
    \"description\": \"Designed and implemented a new authentication module using OAuth2 with PKCE flow\",
    \"evidence_date\": \"2026-03-13\",
    \"created_by_user_id\": \"$USER_ID\"
  }" | python -m json.tool
```

### Step 4: List evidence records

List all records, optionally filtering by date range or user:

```bash
# All records
curl -s http://localhost:8000/api/v1/evidence \
  -H "X-API-Key: $API_KEY" | python -m json.tool

# Filter by date range
curl -s "http://localhost:8000/api/v1/evidence?date_from=2026-03-01&date_to=2026-03-31" \
  -H "X-API-Key: $API_KEY" | python -m json.tool

# Filter by user
curl -s "http://localhost:8000/api/v1/evidence?user_id=$USER_ID" \
  -H "X-API-Key: $API_KEY" | python -m json.tool
```

### Step 5: Generate AI description

Trigger the AI service to generate a richer description for an evidence record. Currently uses a placeholder — a real AI provider (Claude, GPT, etc.) can be plugged in later.

```bash
curl -s -X POST http://localhost:8000/api/v1/evidence/{evidence_id}/generate-description \
  -H "X-API-Key: $API_KEY" | python -m json.tool
```

The `ai_description` field will be populated in the response.

### Step 6: Update or delete

```bash
# Update
curl -s -X PUT http://localhost:8000/api/v1/evidence/{evidence_id} \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"description": "Updated description of the work"}' | python -m json.tool

# Delete
curl -s -X DELETE http://localhost:8000/api/v1/evidence/{evidence_id} \
  -H "X-API-Key: $API_KEY"
```

## API Reference

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/v1/organizations` | None | Create organization (returns API key) |
| `POST` | `/api/v1/users` | API key | Create user in organization |
| `GET` | `/api/v1/users` | API key | List users in organization |
| `POST` | `/api/v1/evidence` | API key | Create evidence record |
| `GET` | `/api/v1/evidence` | API key | List evidence (filters: `date_from`, `date_to`, `user_id`, `offset`, `limit`) |
| `GET` | `/api/v1/evidence/{id}` | API key | Get single evidence record |
| `PUT` | `/api/v1/evidence/{id}` | API key | Update evidence record |
| `DELETE` | `/api/v1/evidence/{id}` | API key | Delete evidence record |
| `POST` | `/api/v1/evidence/{id}/generate-description` | API key | Generate AI description |
| `GET` | `/health` | None | Health check |

Full interactive documentation is available at `/docs` (Swagger UI) or `/redoc` when the server is running.

## Configuration

All settings are configured via environment variables (prefixed with `AKUP_`) or a `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `AKUP_DATABASE_URL` | `sqlite+aiosqlite:///./akup.db` | Database connection string |
| `AKUP_ECHO_SQL` | `false` | Log all SQL queries to stdout |

## Database Management

### Creating new migrations

After modifying SQLAlchemy models, generate a new migration:

```bash
uv run alembic revision --autogenerate -m "describe your change"
```

### Applying migrations

```bash
uv run alembic upgrade head
```

### Downgrading

```bash
uv run alembic downgrade -1
```

## Running Tests

Tests use an in-memory SQLite database — no external database needed.

```bash
uv run pytest -v
```

## Project Structure

```
akup/
├── app/
│   ├── main.py             # FastAPI application entry point
│   ├── config.py           # Settings (env vars)
│   ├── database.py         # SQLAlchemy async engine and session
│   ├── dependencies.py     # FastAPI dependencies (DB session, API key auth)
│   ├── models/             # SQLAlchemy ORM models
│   ├── schemas/            # Pydantic request/response models
│   ├── routers/            # API endpoint definitions
│   ├── services/           # Business logic (evidence CRUD, AI integration)
│   └── static/             # Web frontend (HTML, JS, CSS)
├── cli/                    # CLI client (typer + httpx + rich)
│   ├── main.py             # CLI entry point
│   ├── config.py           # ~/.akup/config.json management
│   ├── client.py           # HTTP client wrapper
│   └── commands/           # CLI command groups
├── alembic/                # Database migrations
├── tests/                  # Pytest test suite
├── pyproject.toml          # Dependencies and tool config
└── .env.example            # Environment variable template
```

## License

See [LICENSE](LICENSE).
