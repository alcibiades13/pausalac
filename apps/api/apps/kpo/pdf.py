"""
KPO PDF export (master prompt §20). Reuses the WeasyPrint pattern proven
in apps.invoices.pdf — same money-formatting helper, imported directly
rather than forked.
"""

from django.template.loader import render_to_string
from weasyprint import HTML

from apps.invoices.pdf import format_money


def render_kpo_pdf(company, entries, *, template_name: str = "kpo/pdf/export.html") -> bytes:
    context = {
        "company": company,
        "entries": [
            {
                "sequence_number": entry.sequence_number,
                "entry_date": entry.entry_date,
                "description": entry.description,
                "product_revenue": format_money(entry.product_revenue),
                "service_revenue": format_money(entry.service_revenue),
                "total_revenue": format_money(entry.total_revenue),
            }
            for entry in entries
        ],
    }
    html = render_to_string(template_name, context)
    return HTML(string=html).write_pdf()
