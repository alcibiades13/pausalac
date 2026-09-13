from django.test import TestCase

from apps.accounts.models import User
from apps.audit.context import clear_context, set_context
from apps.audit.models import AuditLogEntry
from apps.audit.services import AuditService
from apps.companies.models import Company


class AuditServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="marko@pausalac.rs", password="s3cr3t-pass")
        self.company = Company.objects.create(name="Firma A")

    def tearDown(self):
        clear_context()

    def test_log_with_explicit_actor(self):
        entry = AuditService.log(
            actor=self.user,
            company=self.company,
            entity_type="invoice",
            entity_id=42,
            action="created",
            new_value={"total": "1000.00"},
        )
        self.assertEqual(entry.actor, self.user)
        self.assertEqual(entry.entity_id, "42")
        self.assertEqual(AuditLogEntry.objects.count(), 1)

    def test_log_falls_back_to_context_actor(self):
        set_context(actor=self.user, request_id="req-123")
        entry = AuditService.log(entity_type="invoice", entity_id=1, action="created")
        self.assertEqual(entry.actor, self.user)
        self.assertEqual(entry.metadata["request_id"], "req-123")

    def test_log_without_actor_or_context_is_system_entry(self):
        entry = AuditService.log(
            entity_type="invoice", entity_id=1, action="auto_generated", source="celery"
        )
        self.assertIsNone(entry.actor)
        self.assertEqual(entry.source, "celery")
