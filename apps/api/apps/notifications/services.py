"""
Notification generation (master prompt §27/§99). Recipients are the
company's active members who hold the given permission — same
"permission as data" philosophy the rest of RBAC already follows.
"""

from django.utils import timezone

from apps.accounts.models import User
from apps.companies.models import Membership

from .models import Notification


class NotificationService:
    @staticmethod
    def notify_company(
        company,
        *,
        event_type: str,
        dedup_key: str,
        priority: str,
        title: str,
        message: str,
        action_route: str = "",
        action_query: dict | None = None,
        permission_codename: str = "view_financial_data",
    ) -> None:
        action_query = action_query or {}
        recipients = User.objects.filter(
            memberships__company=company, memberships__status=Membership.Status.ACTIVE
        ).distinct()

        for user in recipients:
            if not user.has_company_permission(company, permission_codename):
                continue

            Notification.objects.get_or_create(
                recipient=user,
                channel=Notification.Channel.IN_APP,
                dedup_key=dedup_key,
                defaults={
                    "company": company,
                    "event_type": event_type,
                    "priority": priority,
                    "title": title,
                    "message": message,
                    "action_route": action_route,
                    "action_query": action_query,
                    "status": Notification.Status.SENT,
                    "sent_at": timezone.now(),
                },
            )

            if priority == Notification.Priority.CRITICAL:
                email_notification, created = Notification.objects.get_or_create(
                    recipient=user,
                    channel=Notification.Channel.EMAIL,
                    dedup_key=dedup_key,
                    defaults={
                        "company": company,
                        "event_type": event_type,
                        "priority": priority,
                        "title": title,
                        "message": message,
                        "action_route": action_route,
                        "action_query": action_query,
                        "status": Notification.Status.PENDING,
                    },
                )
                if created:
                    from .tasks import send_notification_email_task

                    send_notification_email_task.delay(email_notification.id)

    @staticmethod
    def mark_read(notification: Notification) -> Notification:
        if notification.read_at is None:
            notification.read_at = timezone.now()
            notification.save(update_fields=["read_at"])
        return notification
