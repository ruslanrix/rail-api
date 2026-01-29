# Deploy

This repo supports running locally, via Docker, and on Railway.

## Local run

```bash
poetry install
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
