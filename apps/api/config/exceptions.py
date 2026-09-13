"""
Custom DRF exception handler enforcing the API error contract
(master prompt §110):

    {"error": {"code": "...", "message": "...", "request_id": "...", "fields": {...}}}

`fields` is present only for dict-shaped validation errors (serializer
field errors) and is additive to the §110 example — it exists so frontend
forms can render inline, per-field errors (§93) instead of only a single
flattened message losing which field(s) actually failed.

Never expose raw backend errors to users (§56) — this is the one place
that shape gets decided, so individual views don't hand-roll error bodies.
"""

import logging
import uuid

from django.http import Http404
from rest_framework import exceptions as drf_exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger("pausalac.api")

# Serbian, human-readable fallback messages per status family. Individual
# exceptions (ValidationError, PermissionDenied, ...) already carry a
# `detail` we prefer to surface — this is only the last-resort fallback.
_DEFAULT_MESSAGES = {
    400: "Zahtev nije ispravan.",
    401: "Niste prijavljeni.",
    403: "Nemate dozvolu za ovu akciju.",
    404: "Traženi resurs ne postoji.",
    405: "Ova akcija nije dozvoljena.",
    429: "Previše zahteva. Pokušajte ponovo za trenutak.",
    500: "Došlo je do greške. Pokušajte ponovo.",
}


def _error_code(exc: Exception) -> str:
    """A stable machine-readable code frontends can branch on."""
    if isinstance(exc, drf_exceptions.APIException):
        code = getattr(exc, "default_code", None) or exc.__class__.__name__
        return str(code).upper()
    return "SERVER_ERROR"


def _flatten_message(detail) -> str:
    if isinstance(detail, (list, tuple)) and detail:
        return _flatten_message(detail[0])
    if isinstance(detail, dict) and detail:
        return _flatten_message(next(iter(detail.values())))
    return str(detail)


def _extract_fields(detail) -> dict[str, list[str]] | None:
    """
    DRF serializer validation errors arrive as `{"field": [ErrorDetail, ...]}`
    (or nested for nested serializers, not handled here — none of our
    serializers nest yet). Returns None for anything else (a single
    top-level message, a bare list, ...) so `fields` is omitted entirely
    rather than sent as a misleading single-key dict.
    """
    if not isinstance(detail, dict) or not detail:
        return None
    fields: dict[str, list[str]] = {}
    for key, value in detail.items():
        if isinstance(value, (list, tuple)):
            fields[key] = [str(v) for v in value]
        elif isinstance(value, dict):
            return None  # nested serializer errors — not flattened here yet
        else:
            fields[key] = [str(value)]
    return fields


def _is_unmodified_default_detail(exc: Exception) -> bool:
    """
    True when `exc` was raised bare (e.g. `raise exceptions.NotAuthenticated()`)
    so its `.detail` is just DRF's built-in English default — in which case we
    prefer our own Serbian fallback. False when the view raised it with an
    explicit message (already Serbian, see apps/accounts/views.py) or when
    `.detail` is a structured dict/list of serializer field errors, which we
    leave as-is rather than collapsing further.
    """
    if not isinstance(exc, drf_exceptions.APIException):
        return False
    default_detail = getattr(exc, "default_detail", None)
    return default_detail is not None and str(exc.detail) == str(default_detail)


def api_exception_handler(exc, context):
    if isinstance(exc, Http404):
        exc = drf_exceptions.NotFound()
    elif isinstance(exc, PermissionError):
        exc = drf_exceptions.PermissionDenied()

    response = drf_exception_handler(exc, context)
    request_id = str(uuid.uuid4())

    if response is None:
        # Unhandled exception — DRF didn't recognize it. Log full detail
        # server-side, never leak it to the client (§56).
        logger.exception("Unhandled API exception (request_id=%s)", request_id, exc_info=exc)
        return Response(
            {
                "error": {
                    "code": "SERVER_ERROR",
                    "message": _DEFAULT_MESSAGES[500],
                    "request_id": request_id,
                }
            },
            status=500,
        )

    fallback = _DEFAULT_MESSAGES.get(response.status_code, "")
    fields = None
    if _is_unmodified_default_detail(exc):
        # DRF's own generic wording (e.g. "Authentication credentials were
        # not provided.") — swap in the Serbian equivalent (§56/§83/§117).
        # Serializer field-validation messages are left as DRF provides them
        # for now — full copy localization of validators is a later pass;
        # the stable `code` here is what the frontend should key its own
        # localized copy off of for anything more specific.
        message = fallback
    else:
        fields = _extract_fields(response.data)
        message = _flatten_message(response.data) if response.data else fallback

    error = {
        "code": _error_code(exc),
        "message": message or fallback,
        "request_id": request_id,
    }
    if fields:
        error["fields"] = fields

    response.data = {"error": error}
    return response
