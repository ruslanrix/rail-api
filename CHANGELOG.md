# Changelog

## [Unreleased]
### Added
- Module I: auth configuration via env for basic/JWT modes
- Module I: POST /token for issuing JWT access tokens
- Module I: auth protection and tests for POST /notify

## [0.1.3] - 2026-01-22
### Added
- Async endpoints: GET /sleep and POST /notify with validation and tests

## [0.1.2] - 2026-01-21
### Added
- /div endpoint with validation and tests
- Pydantic response models wired to endpoints
- Align 400 error schema with FastAPI payload

## [0.1.1] - 2026-01-20
### Added
- Release process documentation

## [0.1.0] - 2026-01-19
### Added
- FastAPI scaffold with /health, /add, /mul, /sub
- Tests (pytest) and lint/format via ruff
- CI workflow (GitHub Actions)
- Railway deploy support (Procfile / Dockerfile)
