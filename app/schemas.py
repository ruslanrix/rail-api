from __future__ import annotations

from pydantic import BaseModel

from pydantic import Field


class HealthResponse(BaseModel):
    status: str


class ResultResponse(BaseModel):
    result: float


class ErrorResponse(BaseModel):
    detail: str


class SleepResponse(BaseModel):
    slept: float


class NotifyRequest(BaseModel):
    message: str = Field(min_length=1, max_length=200)


class OkResponse(BaseModel):
    ok: bool
