# AGENT.md

## Role
- Agent for `rubika-bot-saas`: deliver production-ready backend changes only, minimal noise, and maximum signal.
- Prefer deterministic, scoped commands and avoid redundant validations.

## Project Scope (Hard Boundaries)
- Stay inside MVP scope:
  - Authentication + Workspace + Workspace membership
  - Channels + Scheduled Posts + Auto Replies + Filters
  - Reports + Webhooks/Events + Worker/Scheduler
- Do not add frontend, payment, AI, external SaaS dependencies, or extra product features.

## Priority Ladder (Production)
1. **Safety and secrets**: keep `.env` on server outside git, no real secrets in logs, rotate/apply Rubika token once.
2. **Reliability**: ensure API, worker, and scheduler run on their systemd units after env updates.
3. **Delivery correctness**: run minimal health/auth smoke and queue/scheduler smoke after each deployment step.
4. **Regression control**: only run focused local checks required for touched area (`ruff`, targeted `pytest`, migration check).
5. **Documentation hygiene**: update only required docs for deployment state and token changes.

## Execution Rules
- Use `rg` and `rg --files` locally for discovery.
- Keep `.env` changes explicit and minimal (single active token, old value commented, backups retained).
- Do not expand scope to unrelated cleanup/refactors.
- Prefer existing scripts in `scripts/` and docs in `docs/` over new tooling.
- Validate only what changed:
  - token/env updates → `systemctl` restart + health/auth smoke
  - code changes → narrow tests around touched modules
- Record final state as: `DONE`, `PARTIAL`, or `BLOCKED` with exact evidence (commands + result).

## Response Style
- Start with result first (what changed and what is still pending).
- Report compact, file-based evidence only.
- Avoid token-heavy narration; keep outputs short and directly actionable.
