"""
Plans and subscriptions (master prompt §50/§104/§105, Phase 5). No real
payment gateway is integrated — none is named anywhere in the spec (§69
lists "payment provider" only as a category of environment secret) — so
`activate_plan`/`cancel` (apps.subscriptions.services) are real, testable
state transitions with no money actually moving, the same "architecture
seam, not a fake integration" stance this project has taken toward SEF/
fiscalization throughout. See docs/decisions-log.md.
"""

from django.db import models

from apps.companies.models import Company


class Plan(models.Model):
    """A purchasable tier. Price lives here, not in frontend code, so it
    can change via /admin/ without a deploy (master prompt §50: "Do not
    hard-code prices into frontend")."""

    class BillingInterval(models.TextChoices):
        MONTHLY = "monthly", "Mesečno"

    identifier = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="RSD")
    billing_interval = models.CharField(
        max_length=20, choices=BillingInterval.choices, default=BillingInterval.MONTHLY
    )
    # Forward-looking seam (§104: "Use backend-authoritative entitlement
    # checks"). Seeded empty — no numeric limits or feature list are
    # given anywhere ("Exact limits are TBD"), and none of §104's own
    # example features (SEF, recurring invoices, advanced analytics)
    # exist in the codebase yet, so pre-populating flags for them would
    # look wired-up without being real.
    entitlements = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField("dostupan za izbor", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "plan"
        verbose_name_plural = "planovi"
        ordering = ["price"]

    def __str__(self) -> str:
        return self.name


class Subscription(models.Model):
    """One row per company — the spec's field list (plan/price/billing
    interval/trial/active/cancelled/expired/grace period) reads as
    evolving states of a single subscription, not a billing-period
    ledger, so this is a plain OneToOne rather than a history table."""

    class Status(models.TextChoices):
        TRIALING = "trialing", "Probni period"
        ACTIVE = "active", "Aktivna"
        GRACE_PERIOD = "grace_period", "Period odlaganja"
        CANCELLED = "cancelled", "Otkazana"
        EXPIRED = "expired", "Istekla"

    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name="subscription")
    plan = models.ForeignKey(
        Plan, on_delete=models.PROTECT, null=True, blank=True, related_name="subscriptions"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TRIALING)

    trial_ends_at = models.DateTimeField()
    # One-time flag, not a Notification row — dedup for the "trial ending
    # soon" sweep, same idea as Notification.dedup_key but scoped to this
    # single row rather than a per-event table.
    trial_warning_sent_at = models.DateTimeField(null=True, blank=True)

    # Snapshotted at activation time, not a live join to Plan.price — same
    # "don't silently rewrite history" discipline as FinancialEvent/
    # KPOEntry/TaxObligation.
    price_snapshot = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # Simplistic (+30 days from activation) — there is no real payment
    # cycle to anchor a genuine billing-period ledger to without a
    # payment gateway, so this isn't one; see docs/decisions-log.md.
    current_period_end = models.DateTimeField(null=True, blank=True)

    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "pretplata"
        verbose_name_plural = "pretplate"

    def __str__(self) -> str:
        return f"{self.company_id} ({self.status})"
