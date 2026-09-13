"""
Regression tests for the API error contract (config/exceptions.py),
discovered while wiring the frontend forms in Phase 1c: field-level
validation errors must survive as `error.fields`, not collapse into a
single flattened message (master prompt §93 — inline, per-field errors).
"""

from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User


class ApiErrorContractTests(TestCase):
    def test_serializer_validation_errors_are_exposed_per_field(self):
        User.objects.create_user(email="marko@pausalac.rs", password="s3cr3t-pass")
        url = reverse("auth-register", kwargs={"version": "v1"})
        # Duplicate email (serializer-level) + too-short password
        # (validator-level) in the same request, on purpose, to exercise
        # both error sources landing in `fields` together.
        response = self.client.post(url, {"email": "marko@pausalac.rs", "password": "a"})

        self.assertEqual(response.status_code, 400)
        body = response.json()["error"]
        self.assertIn("fields", body)
        self.assertIn("email", body["fields"])
        self.assertIn("password", body["fields"])

    def test_generic_exceptions_have_no_fields_key(self):
        url = reverse("auth-me", kwargs={"version": "v1"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertNotIn("fields", response.json()["error"])

    def test_custom_single_field_message_still_reported_as_fields(self):
        url = reverse("auth-verify-email", kwargs={"version": "v1"})
        response = self.client.post(url, {"token": "garbage"})
        self.assertEqual(response.status_code, 400)
        body = response.json()["error"]
        self.assertIn("token", body.get("fields", {}))
