You are working inside this repository.

Goal: fix the described bug with minimal change.

Rules:
- Do not change external behavior unless explicitly requested.
- Do not add new dependencies unless necessary.
- Do not touch secrets, tokens, or deployment credentials.
- Prefer small, reviewable diffs.

Process:
1) Identify the root cause and the smallest fix.
2) Implement the fix.
3) Add/adjust tests if applicable.
4) Ensure these pass locally:
   - make test
   - make lint
   - make fmt

Deliverable:
- A concise git diff and a short explanation (what/why).
