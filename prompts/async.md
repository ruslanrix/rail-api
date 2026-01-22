You are working inside this repository.

Goal: add two async endpoints and tests with minimal change.

Add endpoints:
1) GET /sleep?seconds=1
   - async def
   - sleeps for N seconds (float/int allowed, clamp 0..5)
   - returns {"slept": N}

2) POST /notify
   - async def
   - body: {"message": "<text>"}
   - validate: message length 1..200
   - returns {"ok": true}

Rules:
- Keep existing endpoints unchanged.
- No new runtime dependencies.
- Add tests (pytest) for both endpoints.
- Ensure these pass locally:
  - make test
  - make lint
  - make fmt

Deliverable:
- A concise git diff and short explanation (what/why).
