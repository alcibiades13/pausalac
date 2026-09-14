"""
Onboarding-completion computation (master prompt §34), extracted so both
CompanyViewSet.onboarding (the dedicated endpoint) and
apps.analytics.views.DashboardView (the compact dashboard summary) call
the exact same logic — never two slightly-different ways to compute the
same thing.

Computed on read, never stored, so it can't drift from the records it's
summarizing.
"""


def compute_onboarding_status(company) -> dict:
    # Imports apps.clients.models.Client lazily: companies is a lower-level
    # domain that clients depends on (Client FKs to Company), so reaching
    # "up" into clients here is a deliberate, contained exception for this
    # one cross-domain read, not a module-level coupling — see
    # docs/decisions-log.md.
    from apps.clients.models import Client

    completed = []
    missing = []

    if company.name and company.pib:
        completed.append("company")
    else:
        missing.append("company")

    if company.bank_account:
        completed.append("bank")
    else:
        missing.append("bank")

    if Client.objects.for_company(company).filter(is_active=True).exists():
        completed.append("client")
    else:
        missing.append("client")

    # Not built yet (SEF integration is Phase 4+, Documents is a later
    # Phase 3 domain) — honestly reported as missing rather than silently
    # omitted, matching §34's own example list.
    missing.extend(["sef", "tax_document"])

    total = len(completed) + len(missing)
    percentage = round(len(completed) / total * 100) if total else 0

    return {"completed": completed, "missing": missing, "percentage": percentage}
