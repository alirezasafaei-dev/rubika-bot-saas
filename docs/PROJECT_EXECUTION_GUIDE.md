# Project Execution Guide

این سند مرجع اجرایی اصلی پروژه Rubika Bot SaaS - MVP است.
تمام تصمیم‌های فنی، ساختار کد، API، دیتابیس، تست، امنیت و استقرار باید با این سند و مستندات اصلی پروژه سازگار باشند.

---

## 1. Purpose

هدف این پروژه ساخت یک backend production-ready و self-hostable برای مدیریت کانال‌ها و گروه‌های روبیکا در قالب SaaS است.

این پروژه باید:

- local-first باشد
- بدون وابستگی runtime به سرویس SaaS خارجی اجرا شود
- فقط قابلیت‌های MVP را پیاده‌سازی کند
- از ابتدا امن، تست‌پذیر، قابل استقرار و قابل نگهداری باشد

---

## 2. Agent Role

ایجنت این پروژه یک مجری فنی سختگیر است، نه یک ایده‌پرداز کلی.

ایجنت باید:

- فقط کد واقعی، کامل و قابل اجرا تولید کند
- فقط در محدوده MVP بماند
- از ساده‌ترین راه امن و maintainable استفاده کند
- از حدس زدن یا اضافه کردن قابلیت خارج از مستندات خودداری کند
- هر مرحله را کامل، تست‌پذیر و قابل commit تحویل دهد

ایجنت نباید:

- pseudo-code بنویسد
- placeholder مبهم بگذارد
- قابلیت خارج از scope اضافه کند
- وابستگی runtime به cloud service ایجاد کند
- تصمیم مهم مبهم را بدون هماهنگی نهایی کند

اگر ابهام مهمی وجود داشت، فقط یک سؤال ضروری پرسیده شود.

---

## 3. Locked MVP Scope

فقط قابلیت‌های زیر مجازند:

- Authentication
- Workspaces
- Workspace Membership
- Channels
- Scheduled Posts
- Text Auto Replies
- Filters
- Reports
- Webhooks / Events
- Worker / Scheduler

هر چیزی غیر از این ممنوع است، مگر با تأیید صریح.

### Explicitly Forbidden

- Frontend
- Payment
- Subscription billing
- AI integration
- Media auto reply
- Button or keyboard reply
- Voice processing
- OCR
- Campaign management
- CRM
- Advanced analytics outside MVP
- Third-party auth providers
- External hosted DB/queue/scheduler/auth

---

## 4. Final Tech Stack

استک نهایی و قطعی:
```text
Backend: Python 3.12 + FastAPI
Database: PostgreSQL 16
ORM: SQLAlchemy 2
Migrations: Alembic
Validation: Pydantic v2
Settings: pydantic-settings
Authentication: JWT access/refresh + Argon2
Queue: Redis 7 + RQ
Scheduling: PostgreSQL-backed dispatch logic or lightweight periodic scheduler
App Server (dev): Uvicorn
App Server (prod): Gunicorn + UvicornWorker
Testing: pytest + pytest-asyncio + httpx
Lint/Format: Ruff
Type Checking: MyPy
Dependency Management: uv
Containerization: Docker Compose optional
OS Target: Ubuntu 25.10
Shell Target: zsh
Python Install: pyenv

استفاده از هر تکنولوژی اصلی دیگر بدون تأیید مجاز نیست.

---

## 5. Runtime and Infra Rules

پروژه در runtime باید self-hosted باشد.

### Allowed Runtime Services

- PostgreSQL 16
- Redis 7
- FastAPI app
- RQ worker
- Scheduler process

### Forbidden Runtime Dependencies

- Cloud PostgreSQL
- Cloud Redis
- Cloud auth provider
- Cloud scheduler
- External monitoring as mandatory dependency
- SaaS webhook processors
- AI APIs
- Any external service required for core business flow

### Install-time Access

اتصال خارجی فقط برای نصب dependencyها مجاز است و باید با mirror یا cache قابل جایگزینی باشد.

---

## 6. Project Structure Rules

ساختار پروژه باید ساده، ماژولار و test-friendly باشد.

ساختار پیشنهادی:

text
app/
  api/
v1/
  core/
  db/
  models/
  repositories/
  schemas/
  services/
  workers/
  scheduler/
  integrations/
tests/
alembic/
scripts/
docs/

### Rules

- routeها فقط orchestration سطح HTTP انجام دهند
- business logic در service layer باشد
- queryها واضح و قابل تست باشند
- schemaهای Pydantic از modelهای ORM جدا باشند
- وابستگی‌ها از طریق dependency injection در FastAPI مدیریت شوند
- worker و scheduler مستقل از request lifecycle کار کنند

---

## 7. API Standards

### Base Path

text
/api/v1

### General Rules

- همه endpointها نسخه‌دار باشند
- همه responseها JSON باشند
- pagination برای لیست‌ها با `page` و `limit` انجام شود
- ownership check برای همه resourceهای مرتبط با workspace اجباری است
- endpointها باید idempotency مناسب داشته باشند هرجا لازم است
- validation باید در schema layer انجام شود
- parsing دستی request data تا حد امکان انجام نشود

### Required Pagination Contract

Query params:

text
page >= 1
limit between 1 and 100

Response پیشنهادی:

json
{
  "items": [],
  "page": 1,
  "limit": 20,
  "total": 0
}

### Error Contract

json
{
  "error": {
"code": "STRING_CODE",
"message": "Human readable message",
"details": {}
  }
}

### Status Code Rules

- `200` success
- `201` created
- `204` delete or empty mutation response where appropriate
- `400` malformed request when applicable
- `401` unauthenticated
- `403` forbidden
- `404` not found
- `409` conflict
- `422` validation error
- `500` unexpected internal error

---

## 8. Authentication Standards

Auth باید stateless access + stateful refresh model داشته باشد.

### Required Features

- register
- login
- refresh
- logout
- me

### Security Rules

- password hashing only with Argon2
- access token short-lived
- refresh token revocable
- refresh token persistence in database required
- JWT secret only from env
- token rotation preferred
- revoked or expired refresh tokens must fail cleanly
- password hashes never exposed in API responses

---

## 9. Workspace Ownership and Access Control

همه resourceهای اصلی متعلق به Workspace هستند یا از طریق relation به Workspace می‌رسند.

### Required Rule

کاربر فقط در صورتی به resource دسترسی دارد که عضو همان workspace باشد.

### Suggested Roles

- owner
- admin
- member

### Ownership Rules

- creator of workspace becomes owner
- destructive workspace actions restricted to owner
- workspace-scoped queries must always filter by membership
- direct object fetch without workspace ownership check ممنوع است

---

## 10. Database Standards

### Core Principles

- PostgreSQL 16 only
- SQLAlchemy 2 style
- Alembic migrations mandatory
- no schema drift
- every schema change must have migration
- timestamps mandatory on core tables
- soft delete required where logical deletion is needed

### Minimum Common Columns

برای resourceهای اصلی در صورت نیاز:

text
id
created_at
updated_at
deleted_at

### Required Practices

- foreign keys enforced
- indexes on frequent lookup fields
- unique constraints where business rules require
- transaction boundaries explicit in multi-step operations
- row ownership traceable to workspace
- no hidden implicit writes in random layers

---

## 11. Logging Standards

لاگ‌گیری باید structured و production-safe باشد.

### Rules

- log level از env قابل تنظیم باشد
- request lifecycleهای مهم log شوند
- background jobs log شوند
- webhook processing log شود
- secrets, passwords, raw tokens log نشوند
- stack trace فقط در خطاهای واقعی ثبت شود

---

## 12. Webhook and Event Standards

Webhookها برای دریافت eventهای روبیکا استفاده می‌شوند.

### Rules

- endpoint must verify shared secret
- invalid secret returns 401 or 403 based on design consistency
- raw incoming event should be stored when required by MVP design
- processing result should be traceable
- duplicate delivery handling should be safe
- malformed webhook payload should not crash app
- webhook processing may delegate heavy work to worker if needed

---

## 13. Scheduled Post Standards

Scheduled posts در MVP فقط متنی هستند.

### Rules

- scheduled time must be in the future at creation time
- only active channel members/workspace members can manage them
- scheduler finds due records from database
- due records move to queued state before enqueue
- worker executes send action
- success/failure must be logged
- retry logic limited and explicit
- duplicate queueing must be prevented

### Allowed Statuses

text
pending
queued
sent
failed
cancelled

---

## 14. Text Auto Reply Standards

Auto reply در MVP فقط متنی است.

### Allowed

- text trigger
- text response
- enabled/disabled state
- keyword or exact-match logic مطابق مستندات

### Forbidden

- media reply
- image reply
- file reply
- voice reply
- AI reply
- button reply

### Rules

- trigger matching must be deterministic
- disabled rules must not run
- execution should be logged when required
- priority resolution should follow the simplest documented approach

---

## 15. Filter Standards

Filterها در MVP باید حداقلی و deterministic باشند.

### Possible MVP Types

- forbidden words
- links

### Possible MVP Actions

- delete_message

### Rules

- matching logic باید شفاف و قابل تست باشد
- false positive handling تا حد ممکن ساده ولی مستند باشد
- every filter belongs to a channel and workspace chain
- filter hit logs should be queryable for reports

---

## 16. Report Standards

Reports در MVP باید فقط از داده‌های داخلی سیستم ساخته شوند.

### Allowed Report Areas

- overview
- scheduled posts stats
- auto reply stats
- filter stats

### Rules

- report data must be workspace-scoped
- heavy queries should use indexed fields
- date-range filters اگر در مستندات آمده باشند رعایت شوند
- response must be deterministic and paginated where list output exists

---

## 17. Worker and Scheduler Standards

### Worker

- Redis 7 + RQ only
- jobs must be serializable
- failures logged
- retries explicit
- database session handling in jobs must be isolated and safe

### Scheduler

- can be APScheduler or simple periodic process
- must poll database safely
- must not enqueue same due item multiple times
- should use transaction-safe claiming strategy
- must be restart-safe

---

## 18. Validation Rules

### Input Validation

- همه ورودی‌ها با Pydantic v2 validate شوند
- string lengthها محدود شوند
- enumها صریح باشند
- تاریخ‌ها timezone-aware باشند هرجا لازم است
- invalid foreign ownership should not leak resource existence improperly

### Business Validation

- duplicate names checked where required
- duplicate rubika identifiers checked where required
- invalid state transitions rejected
- scheduling in past rejected
- deleting already deleted resource should behave consistently

---

## 19. Testing Standards

هیچ بخش اصلی بدون تست قابل قبول نیست.

### Required Test Types

- unit tests for critical services where useful
- API tests for all main endpoints
- auth tests
- access control tests
- validation tests
- background job tests
- scheduler dispatch tests
- webhook tests

### Required Commands

bash
uv run ruff check .
uv run mypy app
uv run pytest

### Minimum Expectation

- happy path
- unauthorized access
- forbidden access
- validation failure
- not found
- duplicate/conflict
- background execution success/failure

---

## 20. Environment and Configuration Rules

### Required Files

text
.env.example

### Rules

- all secrets from env
- defaults should be safe for local development
- no secrets committed to git
- config loading must be centralized
- environment-specific branching should stay minimal and explicit

---

## 21. Production Readiness Rules

MVP باید روی یک سرور لینوکسی self-hosted قابل استقرار باشد.

### Required Runtime Processes

- api
- postgres
- redis
- worker
- scheduler

### Required Deliverables

- reproducible install steps
- migration commands
- run commands
- deployment documentation
- process management guidance
- health endpoint
- graceful shutdown where applicable

### Optional but Recommended

- Docker Compose
- systemd service files
- reverse proxy example
- backup notes for PostgreSQL

---

## 22. Response Format Rules for the Agent

هر پاسخ اجرایی ایجنت باید این ساختار را رعایت کند:

- Goal
- Plan
- Commands
- Files
- Run
- Verify
- Commit
- Step Report

توضیح‌ها فارسی باشند.
کد، دستور، نام فایل و commit message انگلیسی باشند.

---

## 23. Definition of Done

یک مرحله زمانی done محسوب می‌شود که:

- کد کامل باشد
- lint پاس شود
- type-check پاس شود
- tests پاس شوند
- migration در صورت نیاز موجود باشد
- فایل‌های جدید کامل باشند
- نحوه اجرا گفته شده باشد
- commit message پیشنهاد شده باشد

### 23.1 Operational Checkpoint: Scheduled Posts & Test Infrastructure

- `tests/test_scheduled_posts.py` شامل create/list/update/cancel/delete/logs flow است و باید همواره پاس شود.
- در تست‌ها، `tests/conftest.py` داده‌های fixture را به‌گونه‌ای می‌سازد که تداخل `UNIQUE` رخ ندهد.
- برای اجرای سریع local باید از SQLite تستی استفاده شود (`TEST_DATABASE_URL`).

#### Commands to run before merge

- `uv run ruff check .`
- `uv run mypy app/`
- `uv run pytest`

---

## 24. Implementation Order

ترتیب اجرا:

1. Bootstrap / infra
2. Config / logging / database / migrations
3. Auth
4. Workspaces
5. Channels
6. Scheduled Posts
7. Text Auto Replies
8. Filters
9. Reports
10. Webhooks / Events
11. Worker / Scheduler
12. Tests / hardening / deployment docs

اگر ترتیب جزئی عوض شد، dependencyهای فنی باید حفظ شوند.

---

## 25. Final Rule

اگر بین سرعت و کیفیت تضاد بود، نسخه ساده‌تر اما production-safe انتخاب شود.
اگر بین قابلیت بیشتر و انطباق با MVP تضاد بود، انطباق با MVP اولویت مطلق دارد.
