# Observability

This project provides minimal observability hooks that are **optional** and **env-driven**.

By default, observability is **disabled** (no structured logging changes, metrics endpoint returns 404).
Enable it by setting `OBS_ENABLED=1`.

## Request correlation (X-Request-ID)

- Every response includes `X-Request-ID`.
- If you pass `X-Request-ID` in the request headers, the same value is reused.
- Otherwise, a random request id is generated.

Example:

```bash
curl -i http://localhost:8000/health
curl -i -H 'X-Request-ID: rid-123' http://localhost:8000/health