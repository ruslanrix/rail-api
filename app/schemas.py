from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class ResultResponse(BaseModel):
    result: float


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
