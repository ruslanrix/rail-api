# Prompts

These prompts are short specs for agents (Codex/Claude) to work in this repo with minimal diffs.

- `release.md` — cut a release (changelog, tag, GitHub release)
- `changelog.md` — update CHANGELOG consistently
- `bugfix.md` — fix a bug with smallest change, keep tests/format/lint green
- `async.md` — implement async changes (prefer minimal refactors; keep sync endpoints stable unless requested)

Rules:
- Prefer small, reviewable diffs.
- Don’t touch secrets/credentials.
- Always run:
  - `make test`
  - `make lint`
  - `make fmt`
