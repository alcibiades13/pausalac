"""
Tax obligation business logic — mirrors apps.invoices.services'
InvoiceService shape (master prompt §112: views stay thin, all
state-changing logic lives in a *Service).
"""

from datetime import date
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.audit.services import AuditService
from apps.limits.models import RegulatoryRule
from apps.limits.rules import get_active_rule

from .models import TaxObligation, TaxResolution
from .scheduling import next_due_date

RATE_IDENTIFIERS = {
    "income_tax_amount": ("income_tax_rate", "porez na prihod"),
    "pio_amount": ("pio_rate", "PIO"),
    "health_amount": ("health_rate", "zdravstveno osiguranje"),
    "unemployment_amount": ("unemployment_rate", "osiguranje za slučaj nezaposlenosti"),
}
RATE_TOLERANCE = Decimal("1.00")


def _iter_month_starts(start: date, end: date):
    year, month = start.year, start.month
    while date(year, month, 1) <= end:
        yield date(year, month, 1)
        if month == 12:
            year, month = year + 1, 1
        else:
            month += 1


class TaxService:
    @staticmethod
    @transaction.atomic
    def create_resolution(
        company,
        *,
        effective_from: date,
        effective_until: date,
        tax_base: Decimal,
        income_tax_amount: Decimal,
        pio_amount: Decimal,
        health_amount: Decimal,
        unemployment_amount: Decimal,
        notes: str = "",
    ) -> TaxResolution:
        if effective_until < effective_from:
            raise ValidationError({"effective_until": "Mora biti posle effective_from."})

        month_starts = list(_iter_month_starts(effective_from, effective_until))
        overlap = TaxObligation.objects.filter(
            company=company, period_start__in=month_starts
        ).exists()
        if overlap:
            raise ValidationError(
                "Već postoji obaveza za jedan od meseci u ovom periodu — "
                "rešenja se ne mogu preklapati."
            )

        resolution = TaxResolution.objects.create(
            company=company,
            effective_from=effective_from,
            effective_until=effective_until,
            tax_base=tax_base,
            income_tax_amount=income_tax_amount,
            pio_amount=pio_amount,
            health_amount=health_amount,
            unemployment_amount=unemployment_amount,
            notes=notes,
        )
        TaxObligation.objects.bulk_create(
            [
                TaxObligation(
                    company=company,
                    resolution=resolution,
                    period_start=month_start,
                    due_date=next_due_date(month_start),
                    income_tax_amount=income_tax_amount,
                    pio_amount=pio_amount,
                    health_amount=health_amount,
                    unemployment_amount=unemployment_amount,
                )
                for month_start in month_starts
            ]
        )
        return resolution

    @staticmethod
    def rate_check_warnings(resolution: TaxResolution) -> list[str]:
        warnings = []
        for field, (identifier, label) in RATE_IDENTIFIERS.items():
            try:
                rule = get_active_rule(identifier, resolution.effective_from)
            except RegulatoryRule.DoesNotExist:
                warnings.append(
                    f"Ne može da se proveri stopa za {label} (nema referentnog pravila)."
                )
                continue
            rate = Decimal(str(rule.config["rate"]))
            expected = (resolution.tax_base * rate).quantize(Decimal("0.01"))
            actual = getattr(resolution, field)
            if abs(expected - actual) > RATE_TOLERANCE:
                warnings.append(
                    f"Iznos za {label} ({actual}) odstupa od očekivanog na osnovu referentne "
                    f"stope ({expected}) — proveri rešenje."
                )
        return warnings

    @staticmethod
    def mark_overdue_all() -> int:
        """Mirrors InvoiceService.mark_overdue_all exactly (apps/invoices/services.py)."""
        candidates = TaxObligation.objects.filter(
            status=TaxObligation.Status.PENDING, due_date__lt=timezone.now().date()
        )
        count = 0
        for obligation in candidates:
            old_status = obligation.status
            obligation.status = TaxObligation.Status.OVERDUE
            obligation.save(update_fields=["status"])
            AuditService.log(
                actor=None,
                company=obligation.company,
                entity_type="tax_obligation",
                entity_id=obligation.id,
                action="marked_overdue",
                old_value={"status": old_status},
                new_value={"status": obligation.status},
                source="celery",
            )
            # Lazy import — see the identical exception documented in
            # InvoiceService.mark_overdue_all (apps/invoices/services.py).
            from apps.notifications.models import Notification
            from apps.notifications.services import NotificationService

            NotificationService.notify_company(
                obligation.company,
                event_type="tax_obligation_overdue",
                dedup_key=f"tax_obligation_overdue:{obligation.id}",
                priority=Notification.Priority.CRITICAL,
                title="Poreska obaveza kasni",
                message=f"Poreska obaveza za {obligation.period_start} kasni sa uplatom.",
                action_route="obligations",
            )
            count += 1
        return count

    @staticmethod
    def mark_paid(obligation: TaxObligation, actor) -> TaxObligation:
        old_status = obligation.status
        obligation.status = TaxObligation.Status.PAID
        obligation.paid_at = timezone.now()
        obligation.save(update_fields=["status", "paid_at"])
        AuditService.log(
            actor=actor,
            company=obligation.company,
            entity_type="tax_obligation",
            entity_id=obligation.id,
            action="marked_paid",
            old_value={"status": old_status},
            new_value={"status": obligation.status},
        )
        return obligation
