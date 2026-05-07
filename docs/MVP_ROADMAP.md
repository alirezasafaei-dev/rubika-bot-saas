# MVP Roadmap

این سند نقشه‌راه اجرایی پروژه Rubika Bot SaaS - MVP است.  
هدف این نقشه‌راه این است که پروژه مرحله‌به‌مرحله، قابل تست، قابل commit و production-oriented پیاده‌سازی شود.

---

## Phase 0 — Standards Lock

### Goal

قفل کردن استانداردهای اجرایی پروژه و جلوگیری از پراکندگی تصمیم‌ها.

### Deliverables
```text
docs/PROJECT_EXECUTION_GUIDE.md
docs/MVP_ROADMAP.md

### Acceptance Criteria

- scope MVP نهایی شده باشد
- استک قطعی ثبت شده باشد
- فرمت پاسخ ایجنت مشخص شده باشد
- قواعد API، DB، Security، Test و Production مشخص شده باشند

### Suggested Commit

bash
git add docs/PROJECT_EXECUTION_GUIDE.md docs/MVP_ROADMAP.md
git commit -m "docs: add execution guide and mvp roadmap"

---

## Phase 1 — Bootstrap

### Goal

ساخت اسکلت واقعی پروژه FastAPI با تنظیمات پایه توسعه.

### Deliverables

text
pyproject.toml
app/__init__.py
app/main.py
app/api/__init__.py
app/api/v1/__init__.py
app/api/v1/router.py
app/core/config.py
app/core/logging.py
app/core/errors.py
app/db/__init__.py
app/db/base.py
app/db/session.py
tests/__init__.py
tests/test_health.py
.env.example
README.md

### Tasks

- initialize project with `uv`
- add FastAPI and core dependencies
- configure Ruff
- configure MyPy
- configure pytest and pytest-asyncio
- add health endpoint
- add centralized settings loader
- add structured logging bootstrap

### Acceptance Criteria

bash
uv run ruff check .
uv run mypy app
uv run pytest
uv run uvicorn app.main:app --reload

health endpoint باید پاسخ سالم بدهد.

### Suggested Commit

bash
git add .
git commit -m "chore: bootstrap backend project"

---

## Phase 2 — Database and Alembic

### Goal

راه‌اندازی PostgreSQL 16، SQLAlchemy 2 و migration system.

### Deliverables

text
alembic.ini
alembic/
app/db/base.py
app/db/session.py

### Tasks

- configure SQLAlchemy engine/session
- configure Alembic env
- define metadata naming conventions
- create initial migration plumbing
- ensure env-driven database URL
- prepare testing strategy for DB-backed tests

### Acceptance Criteria

bash
uv run alembic upgrade head

migration باید بدون خطا اجرا شود.

### Suggested Commit

bash
git add .
git commit -m "chore: configure database and migrations"

---

## Phase 3 — Auth

### Goal

پیاده‌سازی احراز هویت JWT با refresh token revocation.

### Endpoints

text
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
GET  /api/v1/auth/me

### Deliverables

text
users table
refresh_tokens table
auth schemas
auth services
auth routes
auth tests

### Tasks

- user registration
- unique email validation
- Argon2 password hashing
- access token creation
- refresh token creation and persistence
- refresh endpoint with revocation/rotation logic
- logout endpoint
- current user dependency

### Acceptance Criteria

- duplicate email rejected
- invalid password rejected
- me endpoint secured
- refresh token works
- revoked refresh token fails
- tests pass

### Suggested Commit

bash
git add .
git commit -m "feat: implement authentication"

---

## Phase 4 — Workspaces

### Goal

پیاده‌سازی ساخت و مدیریت workspace و membership.

### Endpoints

text
POST   /api/v1/workspaces
GET    /api/v1/workspaces
GET    /api/v1/workspaces/{workspace_id}
PATCH  /api/v1/workspaces/{workspace_id}
DELETE /api/v1/workspaces/{workspace_id}

### Deliverables

text
workspaces table
workspace_members table
workspace schemas
workspace services
workspace routes
workspace tests

### Tasks

- create workspace
- auto-create owner membership
- list only current user workspaces
- retrieve single workspace with membership check
- update workspace fields safely
- soft delete workspace if chosen by design
- role-aware access control foundation

### Acceptance Criteria

- creator becomes owner
- non-member cannot access workspace
- deleted workspace no longer appears in listing
- tests cover ownership checks

### Suggested Commit

bash
git add .
git commit -m "feat: implement workspaces"

---

## Phase 5 — Channels

### Goal

افزودن channel/groupهای روبیکا به هر workspace.

### Endpoints

text
POST   /api/v1/workspaces/{workspace_id}/channels
GET    /api/v1/workspaces/{workspace_id}/channels
GET    /api/v1/workspaces/{workspace_id}/channels/{channel_id}
PATCH  /api/v1/workspaces/{workspace_id}/channels/{channel_id}
DELETE /api/v1/workspaces/{workspace_id}/channels/{channel_id}

### Deliverables

text
channels table
channel schemas
channel services
channel routes
channel tests

### Tasks

- create channel under workspace
- validate workspace membership
- enforce unique rubika chat identifier where required
- update channel config safely
- soft delete or deactivate channel consistently

### Acceptance Criteria

- member of another workspace cannot manage channel
- list endpoint paginated
- duplicate channel identifier rejected correctly
- tests pass

### Suggested Commit

bash
git add .
git commit -m "feat: implement channel management"

---

## Phase 6 — Scheduled Posts API

### Goal

ثبت، ویرایش و مدیریت پست‌های زمان‌بندی‌شده متنی.

### Endpoints

text
POST   /api/v1/workspaces/{workspace_id}/channels/{channel_id}/scheduled-posts
GET    /api/v1/workspaces/{workspace_id}/channels/{channel_id}/scheduled-posts
GET    /api/v1/workspaces/{workspace_id}/channels/{channel_id}/scheduled-posts/{post_id}
PATCH  /api/v1/workspaces/{workspace_id}/channels/{channel_id}/scheduled-posts/{post_id}
DELETE /api/v1/workspaces/{workspace_id}/channels/{channel_id}/scheduled-posts/{post_id}

### Deliverables

text
scheduled_posts table
post_logs table
scheduled post schemas
scheduled post services
scheduled post routes
scheduled post tests

### Tasks

- create text-only scheduled post
- validate future scheduled time
- allow update before send
- cancel/delete safely
- list with pagination and filters if documented
- maintain status transitions

### Acceptance Criteria

- past schedule rejected
- non-member forbidden
- deleted/cancelled posts handled consistently
- status model deterministic
- tests pass

### Suggested Commit

bash
git add .
git commit -m "feat: implement scheduled posts api"

---

## Phase 7 — Worker

### Goal

ایجاد worker واقعی برای jobهای پس‌زمینه.

### Deliverables

text
app/workers/queue.py
app/workers/jobs.py
scripts/run_worker.py
worker tests

### Tasks

- configure Redis connection
- configure RQ queue
- implement send scheduled post job
- open isolated DB session in worker jobs
- update scheduled post status
- write post logs for success/failure
- limited retry strategy

### Acceptance Criteria

- worker process starts
- enqueued job executes
- success and failure persisted
- tests for core job path pass

### Suggested Commit

bash
git add .
git commit -m "feat: add worker for scheduled posts"

---

## Phase 8 — Scheduler

### Goal

اسکن پست‌های موعدرسیده و enqueue کردن ایمن آن‌ها.

### Deliverables

text
app/scheduler/service.py
scripts/run_scheduler.py
scheduler tests

### Tasks

- periodically query due pending posts
- claim rows safely
- mark claimed posts as queued
- enqueue RQ jobs
- prevent duplicate dispatch
- make scheduler restart-safe

### Acceptance Criteria

- due posts dispatched once
- non-due posts not dispatched
- duplicate enqueue prevented
- tests cover concurrency-safe flow as much as practical

### Suggested Commit

bash
git add .
git commit -m "feat: add scheduler dispatcher"

---

## Phase 9 — Text Auto Replies

### Goal

پیاده‌سازی ruleهای پاسخ خودکار متنی.

### Endpoints

text
POST   /api/v1/workspaces/{workspace_id}/channels/{channel_id}/auto-replies
GET    /api/v1/workspaces/{workspace_id}/channels/{channel_id}/auto-replies
GET    /api/v1/workspaces/{workspace_id}/channels/{channel_id}/auto-replies/{rule_id}
PATCH  /api/v1/workspaces/{workspace_id}/channels/{channel_id}/auto-replies/{rule_id}
DELETE /api/v1/workspaces/{workspace_id}/channels/{channel_id}/auto-replies/{rule_id}

### Deliverables

text
auto_reply_rules table
auto_reply_keywords table
auto_reply_logs table
auto reply schemas
auto reply services
auto reply routes
auto reply tests

### Tasks

- create rule
- attach keywords or trigger config
- define text response
- enable/disable rule
- list and retrieve rules
- delete rule safely

### Acceptance Criteria

- only text response allowed
- invalid empty triggers rejected
- disabled rules remain inactive
- tests pass

### Suggested Commit

bash
git add .
git commit -m "feat: implement text auto replies"

---

## Phase 10 — Filters

### Goal

پیاده‌سازی filterهای ساده MVP برای پیام‌های ورودی.

### Endpoints

text
POST   /api/v1/workspaces/{workspace_id}/channels/{channel_id}/filters
GET    /api/v1/workspaces/{workspace_id}/channels/{channel_id}/filters
GET    /api/v1/workspaces/{workspace_id}/channels/{channel_id}/filters/{filter_id}
PATCH  /api/v1/workspaces/{workspace_id}/channels/{channel_id}/filters/{filter_id}
DELETE /api/v1/workspaces/{workspace_id}/channels/{channel_id}/filters/{filter_id}

### Deliverables

text
message_filters table
filter_logs table
filter schemas
filter services
filter routes
filter tests

### Tasks

- create forbidden-word filter
- create link filter if within MVP docs
- define deterministic action model
- enable/disable filter
- list/retrieve/delete filters

### Acceptance Criteria

- unsupported filter/action rejected
- channel ownership enforced
- filter CRUD tested
- tests pass

### Suggested Commit

bash
git add .
git commit -m "feat: implement message filters"

---

## Phase 11 — Webhooks and Event Processing

### Goal

دریافت eventهای روبیکا و اجرای pipeline پردازش پیام.

### Endpoints

text
POST /api/v1/webhooks/rubika/{channel_id}

### Deliverables

text
webhook_events table
message_processing_logs table
webhook schemas
webhook route
processing service
webhook tests

### Tasks

- verify webhook secret
- validate payload
- resolve channel
- store raw event or normalized event per design
- execute filters
- if message not blocked, execute auto reply matching
- persist processing logs

### Acceptance Criteria

- invalid secret rejected
- malformed payload rejected safely
- filter executes before auto reply
- processing trace stored
- tests pass

### Suggested Commit

bash
git add .
git commit -m "feat: implement webhook event processing"

---

## Phase 12 — Reports

### Goal

ساخت گزارش‌های پایه workspace-scoped.

### Endpoints

text
GET /api/v1/workspaces/{workspace_id}/reports/overview
GET /api/v1/workspaces/{workspace_id}/reports/scheduled-posts
GET /api/v1/workspaces/{workspace_id}/reports/auto-replies
GET /api/v1/workspaces/{workspace_id}/reports/filters

### Deliverables

text
report services
report routes
report schemas
report tests

### Tasks

- overview metrics
- scheduled posts counters
- sent/failed counters
- auto reply hit counters
- filter hit counters
- paginated list outputs where necessary

### Acceptance Criteria

- all results restricted to current workspace
- metrics derived from internal tables only
- tests verify access control and values

### Suggested Commit

bash
git add .
git commit -m "feat: implement reports"

---

## Phase 13 — API Hardening

### Goal

یکپارچه‌سازی رفتار API و کاهش edge-caseهای ناامن.

### Deliverables

text
centralized error handlers
standardized pagination helpers
shared dependencies
additional tests

### Tasks

- unify error response shape
- unify validation handling
- finalize pagination helpers
- harden ownership checks
- handle soft-delete consistently
- improve not-found vs forbidden behavior where needed
- review logging redaction

### Acceptance Criteria

bash
uv run ruff check .
uv run mypy app
uv run pytest

همه endpointهای اصلی باید contract سازگار داشته باشند.

### Suggested Commit

bash
git add .
git commit -m "refactor: harden api contracts and access control"

---

## Phase 14 — Deployment and Operations Docs

### Goal

آماده‌سازی اجرای واقعی پروژه روی محیط self-hosted.

### Deliverables

text
README.md
docs/deployment.md
.env.example
scripts/run_api.sh
scripts/run_worker.sh
scripts/run_scheduler.sh
docker-compose.yml
systemd/

### Tasks

- write local setup instructions
- write production run instructions
- document migration workflow
- add optional Docker Compose
- add optional systemd units
- provide example Gunicorn command
- provide backup/restore notes if relevant

### Acceptance Criteria

- fresh developer can run app locally from docs
- runtime services and commands documented
- no undocumented required secret remains

### Suggested Commit

bash
git add .
git commit -m "docs: add deployment and operations guide"

---

## Phase 15 — Final Verification

### Goal

بستن MVP با verification واقعی.

### Required Verification Commands

bash
uv run ruff check .
uv run mypy app
uv run pytest
uv run alembic upgrade head

### Final Manual Checks

- auth flow works
- workspace isolation works
- channels scoped correctly
- scheduled posts create/update/delete work
- scheduler dispatches due jobs
- worker processes jobs
- auto replies text-only work
- filters execute correctly
- webhook secret validation works
- reports return workspace-scoped data

### Suggested Commit

bash
git add .
git commit -m "chore: finalize mvp verification"

---

## Done Criteria for Entire MVP

MVP done است اگر:

- فقط scope مجاز MVP پیاده‌سازی شده باشد
- runtime کاملاً self-hosted باشد
- PostgreSQL و Redis local/self-hosted باشند
- API زیر `/api/v1` در دسترس باشد
- migrations سالم باشند
- tests اصلی پاس شوند
- lint و type-check پاس شوند
- worker و scheduler اجرا شوند
- docs اجرای واقعی پروژه را پوشش دهند

---

## Recommended Execution Order Summary

text
0. Standards
1. Bootstrap
2. Database
3. Auth
4. Workspaces
5. Channels
6. Scheduled Posts API
7. Worker
8. Scheduler
9. Text Auto Replies
10. Filters
11. Webhooks / Event Processing
12. Reports
13. API Hardening
14. Deployment Docs
15. Final Verification

---

## Realistic Timeline

### Lean but serious MVP

text
10 to 14 working days

### Production-oriented MVP with stronger tests and ops docs

text
15 to 22 working days

پیشنهاد این پروژه: مسیر production-oriented.


Run  
```bash
$EDITOR docs/PROJECT_EXECUTION_GUIDE.md
$EDITOR docs/MVP_ROADMAP.md
