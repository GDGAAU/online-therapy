"""
core/exceptions.py
===================
Centralised DRF exception handler.

All API errors return a consistent envelope:
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Human-readable summary.",
        "detail": { ...field-level errors or plain string... }
    }
}
"""

import logging
from django.http import Http404
from django.core.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotAuthenticated,
    ValidationError,
    PermissionDenied as DRFPermissionDenied,
    NotFound,
    Throttled,
)

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Wraps DRF's default exception handler to produce a unified error shape.
    """
    # Let DRF handle it first so we get a Response object back
    response = drf_exception_handler(exc, context)

    # Map Django core exceptions → DRF equivalents
    if response is None:
        if isinstance(exc, Http404):
            exc = NotFound()
        elif isinstance(exc, PermissionDenied):
            exc = DRFPermissionDenied()
        else:
            logger.exception("Unhandled server error: %s", exc)
            return Response(
                {
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "An unexpected error occurred.",
                        "detail": None,
                    }
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        response = drf_exception_handler(exc, context)

    # Build canonical error code from exception class name
    code = _to_screaming_snake(type(exc).__name__)

    # ValidationError surfaces field-level details; everything else is a string
    detail = exc.detail if hasattr(exc, "detail") else str(exc)

    response.data = {
        "error": {
            "code": getattr(exc, "default_code", code).upper(),
            "message": _flatten_message(detail),
            "detail": detail,
        }
    }
    return response


# ─── Helpers ────────────────────────────────────────────────

def _to_screaming_snake(name: str) -> str:
    """AuthenticationFailed → AUTHENTICATION_FAILED"""
    import re
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).upper()


def _flatten_message(detail) -> str:
    """Return the first human-readable string from DRF detail structures."""
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list):
        return _flatten_message(detail[0]) if detail else "An error occurred."
    if isinstance(detail, dict):
        first_val = next(iter(detail.values()), "An error occurred.")
        return _flatten_message(first_val)
    return str(detail)
