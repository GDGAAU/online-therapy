"""
core/middleware.py
==================
Custom Django middleware.

RequestLoggingMiddleware: Logs request method, path, status code, and
execution time. In DEBUG mode it also appends a _debug block to JSON
responses — mirroring the Hono debugMode middleware in the original spec.
"""

import time
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """
    Logs every request with method, path, status, and elapsed ms.

    When DEBUG=True, JSON responses get a `_debug` block injected:
    {
        ...original body...,
        "_debug": { "executionTimeMs": "4.23", ...extra data set by views... }
    }

    Views can attach extra debug data via:
        request._debug = {"query_count": 3}
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.perf_counter()
        request._debug = {}  # views may populate this

        response = self.get_response(request)

        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.debug(
            "[%s] %s %s — %.2fms",
            response.status_code,
            request.method,
            request.path,
            elapsed_ms,
        )

        if settings.DEBUG and self._is_json(response):
            try:
                data = json.loads(response.content)
                if isinstance(data, dict):
                    data["_debug"] = {
                        "executionTimeMs": f"{elapsed_ms:.2f}",
                        **request._debug,
                    }

                response.content = json.dumps(data)
                response["Content-Length"] = len(response.content)

            except (json.JSONDecodeError, AttributeError):
                pass  # Never crash on debug injection failure

        return response

    @staticmethod
    def _is_json(response) -> bool:
        content_type = response.get("Content-Type", "")
        return "application/json" in content_type