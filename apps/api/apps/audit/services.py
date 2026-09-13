"""
Explicit audit logging (master prompt §112: named service layer, not a
blanket signal-based auto-logger). Domain services in later phases
(InvoiceService, PaymentService, ...) call `AuditService.log()` directly
at the point a business-meaningful change happens, so entries carry real
old/new-value diffs instead of whatever a generic post_save signal could
infer.
"""

from __future__ import annotations

from typing import Any

from .context import get_current_actor, get_current_request_id
from .models import AuditLogEntry


class AuditService:
    @staticmethod
    def log(
        *,
        entity_type: str,
        entity_id: Any,
        action: str,
        actor=None,
        company=None,
        old_value: dict | None = None,
        new_value: dict | None = None,
        source: str = "api",
        metadata: dict | None = None,
    ) -> AuditLogEntry:
        if actor is None:
            actor = get_current_actor()
        actor = actor if getattr(actor, "is_authenticated", False) else None

        entry_metadata = dict(metadata or {})
        request_id = get_current_request_id()
        if request_id:
            entry_metadata.setdefault("request_id", request_id)

        return AuditLogEntry.objects.create(
            actor=actor,
            company=company,
            entity_type=entity_type,
            entity_id=str(entity_id),
            action=action,
            old_value=old_value,
            new_value=new_value,
            source=source,
            metadata=entry_metadata,
        )
