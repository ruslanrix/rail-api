# Security (practical minimum)

This project uses env-driven security defaults. No secrets are committed to git.

## CORS

By default, CORS is disabled (no CORS middleware).
Enable it only when you need browser-based clients.

### Enable allowlist

Set:

- `CORS_ALLOW_ORIGINS` — comma-separated origins, e.g. `https://example.com,https://admin.example.com`

Optional:

- `CORS_ALLOW_ORIGIN_REGEX` — regex for origins (use carefully)
- `CORS_ALLOW_CREDENTIALS` — `true/false` (default false)
- `CORS_ALLOW_METHODS` — default `GET,POST,PUT,PATCH,DELETE,OPTIONS`
- `CORS_ALLOW_HEADERS` — default `Authorization,Content-Type,X-Request-ID`

Notes:
- Prefer explicit allowlist over `*`.
- Avoid enabling credentials unless strictly needed.

## Recommended security headers (at the edge)

Prefer setting these in your reverse proxy / platform (Railway / ingress):

- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY` (or `SAMEORIGIN` if you embed)
- `Referrer-Policy: no-referrer` (or `strict-origin-when-cross-origin`)
- `Content-Security-Policy` (app-specific; start with a restrictive baseline)

## Rate limiting approach

The API currently does not enforce rate limits in-process (keeps deps minimal).
Recommended approach:
- Apply rate limiting at the edge (CDN / reverse proxy / gateway).
- If you need per-route limits, add it explicitly with a dedicated component and tests.

## PR checklist (agents)

- [ ] Input validation: request models cover required fields and constraints.
- [ ] Auth: protected endpoints require correct auth mode; no accidental open access.
- [ ] Secrets: no credentials/tokens committed; `.env` not committed.
- [ ] Error leakage: 500s do not expose stack traces or internal details.
- [ ] CORS: allowlist is explicit; no wildcard unless intended.
- [ ] Dependencies: no unnecessary new deps; check for known-vuln updates if added.