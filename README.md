# Rubika Bot SaaS MVP Backend

A local-first, self-hostable backend API for managing Rubika bot automation workflows.

This project provides the backend foundation for a Rubika bot management SaaS MVP, including workspace management, channel management, scheduled posts, auto-replies, message filters, reporting, and event processing.

The project is designed to be implemented incrementally through clearly defined MVP phases.

---

## Table of Contents

- [Overview](#overview)
- [MVP Scope](#mvp-scope)
- [Current Implementation Status](#current-implementation-status)
- [Core Principles](#core-principles)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [API Versioning](#api-versioning)
- [Environment Configuration](#environment-configuration)
- [Local Development Setup](#local-development-setup)
- [Running the Application](#running-the-application)
- [Database and Migrations](#database-and-migrations)
- [Background Jobs](#background-jobs)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [API Documentation](#api-documentation)
- [Development Rules](#development-rules)
- [Git Workflow](#git-workflow)
- [License](#license)

---

## Overview

Rubika Bot SaaS MVP Backend is a backend service for managing automation features related to Rubika bots and channels.

The system is intended to support:

- User authentication
- Workspace-based resource ownership
- Rubika channel registration and management
- Scheduled message publishing
- Auto-reply rules
- Message filtering rules
- Basic reporting
- Background job processing
- Internal event/webhook handling

The backend is designed as a modular monolithic application for the MVP stage. This keeps the system simple, maintainable, and deployable on a single server while preserving clean internal boundaries for future growth.

---

## MVP Scope

The MVP focuses on the minimum set of backend features required to manage Rubika bot automation in a reliable and production-oriented way.

The expected MVP modules are:

1. Project bootstrap and infrastructure
2. Configuration and application setup
3. Database setup and migrations
4. Authentication
5. Workspace management
6. Channel management
7. Scheduled posts
8. Auto-replies
9. Message filters
10. Background jobs
11. Reports
12. Events and webhook-style processing
13. API validation and error handling
14. Production readiness
15. Final verification

The exact implementation order and acceptance criteria should follow the project roadmap documents.

---

## Current Implementation Status

This repository may be implemented phase by phase.

Depending on the current development phase, not all documented MVP features may be available yet.

Use the following sources as implementation references:

- `README.md` for setup and project overview
- `PROJECT_EXECUTION_GUIDE.md` for execution standards
- `MVP_ROADMAP.md` for implementation phases and acceptance criteria
- `openapi.yaml` for API contract, when available

If there is a conflict between documentation files, the execution guide and roadmap should be treated as the primary authority.

---

## Core Principles

This project follows these principles:

- Local-first development
- Self-hostable runtime
- No mandatory external SaaS dependency
- Modular monolith for MVP
- Clear API versioning
- Environment-based configuration
- Strong validation at API boundaries
- Centralized error handling
- Structured logging
- Database migrations from the beginning
- Automated tests for implemented features
- Production-oriented defaults
- Small, focused commits per implementation phase

---

## Architecture

The MVP backend should be implemented as a modular FastAPI application.

High-level architecture:

```text
Client / API Consumer
        |
        v
FastAPI Application
        |
        v
API Routers (/api/v1)
        |
        v
Services / Business Logic
        |
        v
Repositories / Database Access
        |
        v
PostgreSQL

Background processing, where required, should use Redis and RQ:

text
FastAPI API
   |
   | enqueue job
   v
Redis Queue
   |
   v
Worker Process
   |
   v
PostgreSQL / Internal Services

The application should not be split into microservices during the MVP unless explicitly required by the roadmap.

---

## Tech Stack

Mandatory backend stack:

| Area | Technology |
| --- | --- |
| Language | Python 3.12 |
| API Framework | FastAPI |
| ASGI Server | Uvicorn |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2 |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Settings | pydantic-settings |
| Auth | JWT access/refresh tokens |
| Password Hashing | Argon2 |
| Background Jobs | Redis 7 + RQ |
| Testing | pytest, pytest-asyncio, httpx |
| Linting / Formatting | Ruff |
| Type Checking | MyPy |
| Dependency Management | uv |
| API Schema | OpenAPI |

---

## Project Structure

Recommended project layout:

text
.
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           └── health.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── errors.py
│   │   ├── logging.py
│   │   └── security.py
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── session.py
│   │
│   ├── models/
│   ├── schemas/
│   ├── repositories/
│   ├── services/
│   ├── workers/
│   └── tasks/
│
├── alembic/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_health.py
│
├── .env.example
├── .gitignore
├── .python-version
├── alembic.ini
├── openapi.yaml
├── pyproject.toml
└── README.md

The structure may grow as new MVP phases are implemented, but separation of concerns should be maintained.

---

## API Versioning

All public API endpoints must be versioned.

Current API base path:

text
/api/v1

Example health endpoint:

text
GET /api/v1/health

Versioning rules:

- Do not expose unversioned business endpoints
- Keep all v1 routes under `app/api/v1`
- Register v1 routes through a central router
- Keep route handlers thin
- Use schemas for request and response validation

---

## Environment Configuration

Runtime configuration must come from environment variables.

Create a local `.env` file from `.env.example`:

bash
cp .env.example .env

Example environment variables:

env
APP_NAME="Rubika Bot SaaS MVP Backend"
APP_ENV="local"
APP_DEBUG=true
APP_HOST="127.0.0.1"
APP_PORT=8000

API_V1_PREFIX="/api/v1"

DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/rubika_bot"

REDIS_URL="redis://localhost:6379/0"

SECRET_KEY="change-this-secret-in-production"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

LOG_LEVEL="INFO"

Security rules:

- Never commit `.env`
- Never hard-code secrets
- Use strong production secrets
- Keep `.env.example` safe and non-sensitive
- Use environment-specific configuration through variables

---

## Local Development Setup

### 1. Clone the Repository

bash
git clone https://github.com/your-username/rubika-bot-saas-backend.git
cd rubika-bot-saas-backend

### 2. Install Python 3.12

Using `pyenv`:

bash
pyenv install 3.12
pyenv local 3.12

Verify:

bash
python --version

Expected:

text
Python 3.12.x

### 3. Install uv

If `uv` is not installed:

bash
curl -LsSf https://astral.sh/uv/install.sh | sh

Restart the shell if necessary, then verify:

bash
uv --version

### 4. Create Virtual Environment

bash
uv venv
source .venv/bin/activate

### 5. Install Dependencies

If dependencies are already defined in `pyproject.toml`:

bash
uv sync

For a new bootstrap phase, dependencies may be added with:

bash
uv add fastapi uvicorn[standard] sqlalchemy alembic pydantic pydantic-settings psycopg[binary]
uv add --dev pytest pytest-asyncio httpx ruff mypy

### 6. Configure Environment

bash
cp .env.example .env

Edit `.env` according to your local PostgreSQL and Redis setup.

---

## Running the Application

Start the development server:

bash
cp .env.example .env
bash scripts/run_api.sh

Application URL:

text
http://127.0.0.1:8000

API base URL:

text
http://127.0.0.1:8000/api/v1

Health check:

bash
curl http://127.0.0.1:8000/api/v1/health

Expected response format may vary by phase, but should be a successful JSON response.

For production-style run:

```bash
uv run gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000
```

Deployment operations are documented in `docs/deployment.md`.

---

## Database and Migrations

The project uses PostgreSQL and Alembic for migrations.

Typical local database URL:

env
DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/rubika_bot"

Create a migration:

bash
uv run alembic revision --autogenerate -m "create initial tables"

Apply migrations:

bash
uv run alembic upgrade head

Rollback one migration:

bash
uv run alembic downgrade -1

Check current migration:

bash
uv run alembic current

Database rules:

- All schema changes must be represented by migrations
- Do not modify production database schema manually
- Keep SQLAlchemy models and Alembic migrations aligned
- Use PostgreSQL-compatible field types
- Add indexes where required by query patterns

---

## Background Jobs

Background jobs are in roadmap phase and currently have placeholder launchers.

The expected stack is:

- Redis 7
- RQ
- Dedicated worker process

Example Redis URL:

env
REDIS_URL="redis://localhost:6379/0"

Example worker command, when implemented:

bash
bash scripts/run_worker.sh

Example scheduler command, when implemented:

```bash
bash scripts/run_scheduler.sh
```

Background job rules:

- Do not execute long-running work inside HTTP request handlers
- Use jobs for scheduled posts and asynchronous processing
- Keep jobs idempotent where possible
- Log job failures clearly
- Store important job state in PostgreSQL when required

---

## Testing

Run all tests:

bash
uv run pytest

Run tests with verbose output:

bash
uv run pytest -v

Run a specific test file:

bash
uv run pytest tests/test_health.py

Testing rules:

- Every implemented feature should have tests
- API tests should use `httpx` or FastAPI test utilities
- Tests must not depend on external SaaS services
- Use isolated test configuration
- Keep tests deterministic

---

## Code Quality

Run Ruff linting:

bash
uv run ruff check .

Run Ruff formatter:

bash
uv run ruff format .

Check formatting without modifying files:

bash
uv run ruff format --check .

Run MyPy:

bash
uv run mypy .

Recommended full verification before commit:

bash
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest

All checks should pass before merging or moving to the next implementation phase.

---

## API Documentation

The API contract may be provided in:

text
openapi.yaml

When the FastAPI application is running, interactive documentation is available at:

text
http://127.0.0.1:8000/docs

OpenAPI JSON:

text
http://127.0.0.1:8000/openapi.json

API documentation rules:

- Keep implementation aligned with OpenAPI
- Use clear request and response schemas
- Return consistent error responses
- Do not expose internal implementation details in public API responses
- Keep route naming consistent and predictable

---

## Development Rules

General implementation rules:

- Implement one roadmap phase at a time
- Do not implement future-phase features early
- Keep changes small and reviewable
- Use production-oriented code from the beginning
- Do not add placeholder code
- Do not leave TODO comments in committed code
- Do not hard-code secrets or environment-specific values
- Keep business logic outside route handlers
- Keep database access isolated from API handlers
- Add tests with each feature
- Keep Ruff, MyPy, and pytest passing

Runtime rules:

- The project must remain local-first
- The project must remain self-hostable
- No mandatory external SaaS dependency is allowed
- PostgreSQL and Redis are acceptable local/self-hosted services
- Configuration must be environment-driven

---

## Git Workflow

Recommended branch naming:

text
phase-01-bootstrap
phase-02-database
feature/auth
fix/health-endpoint

Recommended commit format:

text
type(scope): short description

Examples:

bash
git commit -m "chore: bootstrap FastAPI project"
git commit -m "feat(auth): add login endpoint"
git commit -m "test(health): add health endpoint test"
git commit -m "fix(config): validate database url"

Before committing, run:

bash
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest

---

## License

This project is licensed under the MIT License.

See the `LICENSE` file for details.


---
