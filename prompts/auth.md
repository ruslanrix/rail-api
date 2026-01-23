You are working inside this repository (rail-api).

Module: I — Auth (basic auth/JWT) & security basics.
Do NOT rename or modify completed modules A–H. Add new work only as Module I.

Goal:
- Add authentication capabilities (Basic Auth and JWT Bearer) with minimal, reviewable diffs.
- Do NOT break existing public endpoints behavior unless explicitly stated.

Non-goals:
- No database, no user registration, no OAuth providers.
- No complex RBAC.

Plan (implementation requirements):
1) Add config (env-driven):
   - AUTH_MODE: "none" | "basic" | "jwt"
   - BASIC_USER / BASIC_PASS (for basic)
   - JWT_SECRET / JWT_TTL_SECONDS (for jwt)
   - Keep safe defaults (AUTH_MODE=none).
2) Implement Basic Auth using FastAPI security utilities.
   - Protected endpoint(s): at least POST /notify must require auth when AUTH_MODE=basic or jwt.
3) Implement JWT (Bearer) auth:
   - Add POST /token endpoint that returns access token (JWT).
   - Token payload: "sub" (username), "exp" (expiry).
   - Use HS256.
   - If JWT_SECRET missing but AUTH_MODE=jwt -> fail fast (clear error on startup) or return 500 with clear message (choose minimal).
   - New dependency is allowed ONLY if necessary for JWT (prefer PyJWT).
4) Security basics:
   - Return proper 401 with WWW-Authenticate header where applicable.
   - Do not log secrets/tokens.
   - Keep .env.example placeholders (no real secrets).
5) Update schemas:
   - Add TokenResponse model and error responses if needed.
6) Tests:
   - No auth -> 401 for protected endpoints
   - Basic valid/invalid
   - JWT valid/invalid/expired (expiry test can be minimal)
7) Local checks must pass:
   - make test
   - make lint
   - make fmt
8) Update CHANGELOG.md under [Unreleased] with 2–4 bullets.

Deliverable:
- Provide a concise git diff and short explanation (what/why).
- Include exact commands run and resulting outputs for checks (copy/paste friendly).