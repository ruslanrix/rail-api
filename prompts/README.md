## Prompts index

These prompts are the “contracts” for agents (Codex/Claude): follow the goal, rules, process, and deliverables exactly. Prefer small PRs with minimal diffs.

### General / reusable
- `bugfix.md` — Minimal-diff bugfix workflow (root cause → fix → tests → make test/lint/fmt).
- `changelog.md` — Update CHANGELOG using Keep a Changelog style, keep “Unreleased” tidy.
- `release.md` — Release procedure (branch/PR → tag → GitHub Release), consistent versioning.
- `async.md` — Async module spec (reference for async endpoints patterns & tests).

### Modules (specs)
- `module-i.md` — Module I: Auth & security basics (protect `/notify`, Basic + JWT, `/token`, env config, tests).
- `module-j.md` — Module J: Observability (logging/metrics/tracing basics) + verification checklist.
- `module-k.md` — Module K: App structure & routers
- `module-l.md` — Module L: Config & settings (env-first)
- `module-m.md` — Module M: Persistence minimal (DB + migrations)
- `module-n.md` — Module N: External integrations (HTTP client)
- `module-o.md` — Module O: Background jobs

### Next modules (planned)
- `module-p.md` — Module P: Testing level-up
- `module-q.md` — Module Q: Deployment hardening
- `module-r.md` — Module R: Observability+
- `module-s.md` — Module S: Security+ (practical minimum)
- `module-t.md` — Module T: Capstone: production-ready template stack

> Tip: keep this file updated whenever you add/rename a prompt, so agents can discover the latest canonical specs quickly.
