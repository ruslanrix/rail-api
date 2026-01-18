FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Poetry
RUN pip install --no-cache-dir poetry

# deps first (лучше кэш)
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi --no-root

# app code
COPY . .

# Railway/Fly/etc обычно дают PORT
CMD ["sh", "-c", "poetry run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
