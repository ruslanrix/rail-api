# Agent instructions (hello-api)

## Goal
Make small, verifiable changes. Preserve existing behavior unless explicitly asked.

## Commands (local)
- Install deps: `poetry install --no-root`
- Run dev server: `make dev`
- Health check: `make health`

## Project notes
- App entry: `main.py` (`app` variable)
- Endpoints: `/` and `/health`

## How to work (required)
- For non-trivial tasks: propose a short plan (2–5 steps).
- Keep diffs minimal and localized.
- After changes, run `make health` (and mention results).
- Avoid adding new dependencies unless requested.

## Git hygiene
- Do not commit `.venv/`
