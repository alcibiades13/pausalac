"""
Company-scoped permission codenames per role (master prompt §30) as data,
not scattered if/else — the same philosophy the rules engine applies to
regulatory numbers, applied here to RBAC.

`ACCOUNTANT`/`ACCOUNTANT_ADMIN` splits are placeholders: real granularity
matters once Phase 4 builds the accountant experience against this. Widen
or narrow the sets here as that phase clarifies real needs — this dict is
the only place that should ever need to change.
"""

from apps.companies.models import Membership

Role = Membership.Role

ALL_PERMISSIONS: set[str] = {
    "view_financial_data",
    "create_invoice",
    "edit_invoice",
    "cancel_invoice",
    "view_documents",
    "upload_documents",
    "manage_tax_obligations",
    "view_audit",
    "manage_users",
    "manage_subscriptions",
    "manage_rules",
}

ROLE_PERMISSIONS: dict[str, set[str]] = {
    Role.OWNER: set(ALL_PERMISSIONS),
    Role.ACCOUNTANT_ADMIN: {
        "view_financial_data",
        "create_invoice",
        "edit_invoice",
        "view_documents",
        "upload_documents",
        "manage_tax_obligations",
        "view_audit",
    },
    Role.ACCOUNTANT: {
        "view_financial_data",
        "view_documents",
        "view_audit",
    },
}
