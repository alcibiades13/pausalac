"""
Per-request context (current actor + request id) so `AuditService.log()`
(services.py) doesn't need `request` threaded through every domain-service
call site by hand. Bound/reset by `AuditContextMiddleware` on every request;
Celery tasks set their own context explicitly (there is no request there).
"""

import uuid
from contextvars import ContextVar

_current_actor: ContextVar = ContextVar("audit_current_actor", default=None)
_current_request_id: ContextVar = ContextVar("audit_current_request_id", default=None)


def get_current_actor():
    return _current_actor.get()


def get_current_request_id():
    return _current_request_id.get()


def set_context(*, actor=None, request_id: str | None = None):
    _current_actor.set(actor)
    _current_request_id.set(request_id)


def clear_context():
    _current_actor.set(None)
    _current_request_id.set(None)


class AuditContextMiddleware:
    """Binds the authenticated user + a request id for the audit context,
    for the duration of one request only."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        actor = getattr(request, "user", None)
        if actor is not None and not actor.is_authenticated:
            actor = None
        set_context(actor=actor, request_id=str(uuid.uuid4()))
        try:
            return self.get_response(request)
        finally:
            clear_context()
