from __future__ import annotations

import contextvars
import logging
import os
import sys
import threading
import time
import uuid
from collections import defaultdict

request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")


def obs_enabled() -> bool:
    v = os.getenv("OBS_ENABLED", "")
    return v.lower() in {"1", "true", "yes", "on"}


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:  # pragma: no cover - trivial
        record.request_id = request_id_var.get("-")
        return True


_logging_configured = False


def configure_logging() -> None:
    global _logging_configured
    if _logging_configured:
        return

    # observability optional (off by default)
    if not obs_enabled():
        return

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(RequestIdFilter())
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s %(levelname)s request_id=%(request_id)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
    )
    root_logger.addHandler(handler)
    _logging_configured = True


class Metrics:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._request_counts: dict[tuple[str, str, str], int] = defaultdict(int)
        self._duration_sum: dict[tuple[str, str], float] = defaultdict(float)
        self._duration_count: dict[tuple[str, str], int] = defaultdict(int)

    def record(self, *, method: str, path: str, status: int, duration_s: float) -> None:
        if not obs_enabled():
            return

        key = (method, path, str(status))
        duration_key = (method, path)
        with self._lock:
            self._request_counts[key] += 1
            self._duration_sum[duration_key] += duration_s
            self._duration_count[duration_key] += 1

    def render_prometheus(self) -> str:
        with self._lock:
            request_counts = dict(self._request_counts)
            duration_sum = dict(self._duration_sum)
            duration_count = dict(self._duration_count)

        lines = [
            "# HELP http_requests_total Total HTTP requests.",
            "# TYPE http_requests_total counter",
        ]
        for (method, path, status), value in sorted(request_counts.items()):
            lines.append(
                'http_requests_total{method="%s",path="%s",status="%s"} %s'
                % (method, path, status, value)
            )

        lines.extend(
            [
                "# HELP http_request_duration_seconds_sum Total request duration in seconds.",
                "# TYPE http_request_duration_seconds_sum counter",
            ]
        )
        for (method, path), value in sorted(duration_sum.items()):
            lines.append(
                'http_request_duration_seconds_sum{method="%s",path="%s"} %s'
                % (method, path, value)
            )

        lines.extend(
            [
                "# HELP http_request_duration_seconds_count Total number of requests for duration tracking.",
                "# TYPE http_request_duration_seconds_count counter",
            ]
        )
        for (method, path), value in sorted(duration_count.items()):
            lines.append(
                'http_request_duration_seconds_count{method="%s",path="%s"} %s'
                % (method, path, value)
            )

        return "\n".join(lines) + "\n"


def get_or_create_request_id(request_id_header: str | None) -> str:
    if request_id_header:
        return request_id_header
    return uuid.uuid4().hex


def now() -> float:
    return time.perf_counter()


metrics = Metrics()
