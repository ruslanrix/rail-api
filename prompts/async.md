You are working inside this repository.

Goal: implement Async module (H) with minimal, reviewable changes:
- add async endpoint /sleep
- add endpoint /notify using BackgroundTasks
- add/adjust tests
- keep CI green

Rules:
- Prefer smallest diff.
- Do not add new runtime dependencies unless absolutely necessary.
- Keep behavior explicit and deterministic.
- Update README only if endpoints are not discoverable otherwise.
- Ensure these pass locally:
  - make test
  - make lint
  - make fmt

Implementation details:
1) /sleep
- GET /sleep?ms=...
- Validate: ms must be >= 0 and <= 60000 (60s). If invalid, return HTTP 400.
- Implementation: await asyncio.sleep(ms/1000)
- Response: {"slept_ms": ms}

2) /notify
- GET /notify?msg=...
- Use FastAPI BackgroundTasks:
  - schedule a function that logs the message (logger.info)
- Response immediately: {"queued": true}

3) Tests
- Add tests for /sleep and /notify (use fastapi.testclient).
- For /sleep, keep ms small (e.g., 1–5 ms) to avoid slowing CI.
- Validate 400 paths: /sleep?ms=-1 and /sleep?ms=999999.

Deliverable:
- A concise git diff.
- Short explanation of what changed and why.