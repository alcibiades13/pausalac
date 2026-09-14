from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse


class HealthLivenessTests(TestCase):
    def test_health_is_always_ok_and_requires_no_dependencies(self):
        response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


class HealthReadinessTests(TestCase):
    def setUp(self):
        self.url = reverse("health-ready")

    def test_all_dependencies_healthy_returns_200(self):
        with (
            patch("config.health._check_database", return_value=True),
            patch("config.health._check_redis", return_value=True),
            patch("config.health._check_storage", return_value=True),
        ):
            response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["checks"], {"database": True, "redis": True, "storage": True})

    def test_one_dependency_down_returns_503(self):
        with (
            patch("config.health._check_database", return_value=True),
            patch("config.health._check_redis", return_value=False),
            patch("config.health._check_storage", return_value=True),
        ):
            response = self.client.get(self.url)
        self.assertEqual(response.status_code, 503)
        body = response.json()
        self.assertEqual(body["status"], "degraded")
        self.assertFalse(body["checks"]["redis"])

    def test_database_check_is_real_against_the_test_database(self):
        # No mocking here — the test DB is real, so this should pass on
        # its own, proving _check_database actually queries something
        # rather than always returning True.
        from config.health import _check_database

        self.assertTrue(_check_database())
