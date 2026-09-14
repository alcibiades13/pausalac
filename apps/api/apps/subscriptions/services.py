"""
Subscription lifecycle (master prompt §112: named service layer). See
apps/subscriptions/models.py for why there's no real payment collection
here yet.
"""

from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.analytics.tracking import track_event
from apps.audit.services import AuditService

from .models import Plan, Subscription


class SubscriptionService:
    @staticmethod
    def get_or_create_trial(company) -> Subscription:
        """Called explicitly wherever a real subscription row is actually
        needed: CompanyViewSet.perform_create (so every new company gets
        one immediately) and the subscriptions views themselves (so
        "view/manage my subscription" always has something real to act
        on). Never called as a side effect of an unrelated permission
        check elsewhere — see has_active_access, which deliberately fails
        open instead of auto-provisioning, so other domains' tests never
        need a subscription fixture just because this app exists."""
        subscription, created = Subscription.objects.get_or_create(
            company=company,
            defaults={
                "trial_ends_at": timezone.now() + timedelta(days=settings.SUBSCRIPTION_TRIAL_DAYS)
            },
        )
        if created:
            track_event("trial_started", company=company)
        return subscription

    @staticmethod
    def has_active_access(company) -> bool:
        """Fails open when no Subscription row exists at all — every
        existing test/fixture across the whole suite creates bare
        Company rows directly, never through CompanyViewSet, so none of
        them have a subscription; only a company with an explicit
        cancelled/expired row is ever blocked. `getattr` with a default
        is the idiomatic Django way to probe a reverse OneToOne without
        raising — its descriptor's DoesNotExist subclasses AttributeError
        for exactly this."""
        subscription = getattr(company, "subscription", None)
        if subscription is None:
            return True
        return subscription.status in (
            Subscription.Status.TRIALING,
            Subscription.Status.ACTIVE,
            Subscription.Status.GRACE_PERIOD,
        )

    @staticmethod
    def activate_plan(subscription: Subscription, plan: Plan, actor) -> Subscription:
        old_status = subscription.status
        subscription.plan = plan
        subscription.status = Subscription.Status.ACTIVE
        subscription.price_snapshot = plan.price
        subscription.current_period_end = timezone.now() + timedelta(days=30)
        subscription.cancelled_at = None
        subscription.save(
            update_fields=[
                "plan",
                "status",
                "price_snapshot",
                "current_period_end",
                "cancelled_at",
                "updated_at",
            ]
        )
        AuditService.log(
            actor=actor,
            company=subscription.company,
            entity_type="subscription",
            entity_id=subscription.id,
            action="plan_activated",
            old_value={"status": old_status},
            new_value={"status": subscription.status, "plan": plan.identifier},
        )
        if old_status == Subscription.Status.TRIALING:
            # Only a genuine trial->paid transition is "trial_converted"
            # (master prompt §73) — reactivating from cancelled/expired
            # isn't a trial conversion.
            track_event(
                "trial_converted",
                user=actor,
                company=subscription.company,
                plan=plan.identifier,
            )
        return subscription

    @staticmethod
    def cancel(subscription: Subscription, actor) -> Subscription:
        old_status = subscription.status
        subscription.status = Subscription.Status.CANCELLED
        subscription.cancelled_at = timezone.now()
        subscription.save(update_fields=["status", "cancelled_at", "updated_at"])
        AuditService.log(
            actor=actor,
            company=subscription.company,
            entity_type="subscription",
            entity_id=subscription.id,
            action="cancelled",
            old_value={"status": old_status},
            new_value={"status": subscription.status},
        )
        return subscription

    @staticmethod
    @transaction.atomic
    def expire_trials() -> int:
        """Beat-scheduled sweep (config/celery.py), mirrors
        InvoiceService.mark_overdue_all / TaxService.mark_overdue_all
        exactly."""
        candidates = Subscription.objects.filter(
            status=Subscription.Status.TRIALING, trial_ends_at__lt=timezone.now()
        )
        count = 0
        for subscription in candidates:
            subscription.status = Subscription.Status.EXPIRED
            subscription.save(update_fields=["status", "updated_at"])
            AuditService.log(
                actor=None,
                company=subscription.company,
                entity_type="subscription",
                entity_id=subscription.id,
                action="trial_expired",
                old_value={"status": Subscription.Status.TRIALING},
                new_value={"status": subscription.status},
                source="celery",
            )
            # Lazy import — apps.notifications sits after apps.subscriptions
            # in DOMAIN_APPS, same precedent as InvoiceService/TaxService's
            # own sweeps and apps.accounting.services.
            from apps.notifications.models import Notification
            from apps.notifications.services import NotificationService

            NotificationService.notify_company(
                subscription.company,
                event_type="trial_expired",
                dedup_key=f"trial_expired:{subscription.id}",
                priority=Notification.Priority.CRITICAL,
                title="Probni period je istekao",
                message=(
                    "Tvoj probni period je istekao. Izaberi plan da nastaviš da izdaješ fakture."
                ),
                action_route="subscription",
                permission_codename="manage_subscriptions",
            )
            count += 1
        return count

    @staticmethod
    def send_trial_warnings(*, days_before: int = 3) -> int:
        """Fires once per subscription (trial_warning_sent_at is the
        dedup) — same "don't renotify on every check" rule as §99, just
        enforced on this row instead of Notification's own dedup_key."""
        threshold = timezone.now() + timedelta(days=days_before)
        candidates = Subscription.objects.filter(
            status=Subscription.Status.TRIALING,
            trial_ends_at__lte=threshold,
            trial_ends_at__gt=timezone.now(),
            trial_warning_sent_at__isnull=True,
        )
        count = 0
        for subscription in candidates:
            from apps.notifications.models import Notification
            from apps.notifications.services import NotificationService

            NotificationService.notify_company(
                subscription.company,
                event_type="trial_ending_soon",
                dedup_key=f"trial_ending_soon:{subscription.id}",
                priority=Notification.Priority.ATTENTION,
                title="Probni period uskoro ističe",
                message=(
                    f"Tvoj probni period ističe {subscription.trial_ends_at.date().isoformat()}."
                ),
                action_route="subscription",
                permission_codename="manage_subscriptions",
            )
            subscription.trial_warning_sent_at = timezone.now()
            subscription.save(update_fields=["trial_warning_sent_at", "updated_at"])
            count += 1
        return count
