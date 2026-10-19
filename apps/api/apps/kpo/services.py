"""
KPO generation (master prompt §20: "treba automatski da generiše KPO
entry"). Called from apps.invoices.services.InvoiceService.issue/cancel,
in the same transaction as the FinancialEvent it mirrors — see
docs/decisions-log.md for why this is a real write at issue time, not a
read-time computed view.
"""

from datetime import date
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce, TruncMonth

from apps.invoices.models import Invoice, InvoiceLineItem

from .models import KPOEntry
from .numbering import assign_sequence_number


def monthly_summary(company, year: int) -> list[dict]:
    """Products/services/total per month for `KpoMonthlyBarChart` — reads
    the same `KPOEntry` rows the KPO table itself lists (storno rows
    already store negative product/service amounts, so a plain `Sum`
    nets them out correctly, same as the table's own totals). One row
    per calendar month, even ones with no activity, for a stable X-axis.
    """
    period_start = date(year, 1, 1)
    period_end = date(year, 12, 31)
    rows = (
        KPOEntry.objects.for_company(company)
        .filter(entry_date__gte=period_start, entry_date__lte=period_end)
        .annotate(month=TruncMonth("entry_date"))
        .values("month")
        .annotate(
            products=Coalesce(Sum("product_revenue"), Value(Decimal("0.00"))),
            services=Coalesce(Sum("service_revenue"), Value(Decimal("0.00"))),
        )
    )
    by_month = {row["month"].isoformat(): row for row in rows}

    months: list[dict] = []
    cursor = period_start
    end_marker = date(year, 12, 1)
    while cursor <= end_marker:
        key = cursor.isoformat()
        row = by_month.get(key)
        products = row["products"] if row else Decimal("0.00")
        services = row["services"] if row else Decimal("0.00")
        months.append(
            {"month": key, "products": products, "services": services, "total": products + services}
        )
        cursor = date(cursor.year + 1, 1, 1) if cursor.month == 12 else date(cursor.year, cursor.month + 1, 1)
    return months


def _sum_by_item_type(invoice: Invoice, item_type: str) -> Decimal:
    total = Decimal("0.00")
    for item in invoice.items.all():
        if item.item_type == item_type:
            total += item.line_total
    return total


class KPOService:
    @staticmethod
    @transaction.atomic
    def record_issued(invoice: Invoice) -> KPOEntry:
        product_revenue = _sum_by_item_type(invoice, InvoiceLineItem.ItemType.PRODUCT)
        service_revenue = _sum_by_item_type(invoice, InvoiceLineItem.ItemType.SERVICE)
        sequence_number = assign_sequence_number(invoice.service_date, invoice.company)
        return KPOEntry.objects.create(
            company=invoice.company,
            invoice=invoice,
            sequence_number=sequence_number,
            entry_date=invoice.service_date,
            description=f"Faktura {invoice.invoice_number} — {invoice.client.name}",
            product_revenue=product_revenue,
            service_revenue=service_revenue,
            entry_type=KPOEntry.EntryType.ORIGINAL,
        )

    @staticmethod
    @transaction.atomic
    def record_cancelled(invoice: Invoice) -> KPOEntry | None:
        original = (
            KPOEntry.objects.filter(invoice=invoice, entry_type=KPOEntry.EntryType.ORIGINAL)
            .order_by("-sequence_number")
            .first()
        )
        if original is None:
            # Never issued (or issued before this field existed on an
            # older invoice with no ORIGINAL row) — nothing to reverse.
            return None
        sequence_number = assign_sequence_number(invoice.service_date, invoice.company)
        return KPOEntry.objects.create(
            company=invoice.company,
            invoice=invoice,
            sequence_number=sequence_number,
            entry_date=invoice.service_date,
            description=f"Storno: {original.description}",
            product_revenue=-original.product_revenue,
            service_revenue=-original.service_revenue,
            entry_type=KPOEntry.EntryType.STORNO,
        )
