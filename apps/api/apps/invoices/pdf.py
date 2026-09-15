"""
Invoice PDF rendering (master prompt §12: a reusable template system, not
HTML hard-coded inside invoice business logic — this module and its
template are the only things that know how a PDF is built; services.py
and views.py never touch HTML). §108: deterministic, backend-owned.

Font is a system sans-serif stack, not the web app's Inter — WeasyPrint
needs a locally embeddable font file for reliable custom-font rendering,
and Inter (loaded via packages/config/tokens.css) isn't available to a
server-side renderer. A different font for print vs. screen is normal,
not a design compromise worth chasing font-embedding for right now.
"""

from decimal import Decimal

from django.template.loader import render_to_string
from weasyprint import HTML


def format_money(amount: Decimal) -> str:
    """Serbian convention: dot thousands separator, comma decimal — e.g. 2.840.000,00."""
    return f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def render_invoice_pdf(invoice, *, template_name: str = "invoices/pdf/default.html") -> bytes:
    """
    Renders `invoice` to PDF bytes. `template_name` exists so a second
    layout could be added later without changing this function's
    signature — only one template exists today (master prompt §78: don't
    build the registry/selection machinery before a second template
    justifies it).
    """
    context = {
        "invoice": invoice,
        "company": invoice.company,
        "client": invoice.client,
        "items": [
            {
                "description": item.description,
                "quantity": item.quantity,
                "unit_price": format_money(item.unit_price),
                "line_total": format_money(item.line_total),
            }
            for item in invoice.items.all()
        ],
        "total_formatted": format_money(invoice.total),
        "is_draft": invoice.status == invoice.Status.DRAFT,
        # Phase 6c: Profaktura/Avans reuse this same template rather than
        # a separate one per type (pdf.py's own template_name seam isn't
        # justified yet by anything more than a title/disclaimer change).
        "document_type": invoice.document_type,
        "document_label": invoice.get_document_type_display(),
    }
    html = render_to_string(template_name, context)
    return HTML(string=html).write_pdf()
