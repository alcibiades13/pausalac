"""
Rate limiting (master prompt §48). `throttle_scope = "auth"` on Register/
Login/PasswordResetRequest is the actual abuse-target coverage.

Deliberately exercises the *real* production rate (config/settings/base.py
— currently 10/min) with real repeated requests, rather than
`override_settings` on the nested REST_FRAMEWORK dict: DRF's cached
`api_settings` didn't reliably pick up an overridden `DEFAULT_THROTTLE_RATES`
once enough other test modules had already run in the same session (caught
via full-suite runs failing while every smaller subset passed — a real,
reproduced flake, not a guess) — real requests against the real rate have
no such dependency on settings-reload timing.
"""

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User

# Must match config/settings/base.py's REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["auth"].
AUTH_RATE_PER_MINUTE = 10


class AuthThrottleTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_login_is_rate_limited_after_the_auth_scope_is_exhausted(self):
        User.objects.create_user(email="marko@pausalac.rs", password="s3cr3t-pass")
        url = reverse("auth-login", kwargs={"version": "v1"})
        payload = {"email": "marko@pausalac.rs", "password": "wrong-password"}

        for _ in range(AUTH_RATE_PER_MINUTE):
            response = self.client.post(url, payload, content_type="application/json")
            # 403, not 401: SessionAuthentication has no WWW-Authenticate
            # challenge to issue — same reasoning as the existing "requires
            # authentication" tests elsewhere in this codebase.
            self.assertEqual(response.status_code, 403)

        blocked = self.client.post(url, payload, content_type="application/json")
        self.assertEqual(blocked.status_code, 429)

    def test_register_is_rate_limited_after_the_auth_scope_is_exhausted(self):
        url = reverse("auth-register", kwargs={"version": "v1"})

        for i in range(AUTH_RATE_PER_MINUTE):
            response = self.client.post(
                url,
                {"email": f"user{i}@pausalac.rs", "password": "s3cr3t-pass-123"},
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 201)
            self.client.logout()

        blocked = self.client.post(
            url,
            {"email": "user-blocked@pausalac.rs", "password": "s3cr3t-pass-123"},
            content_type="application/json",
        )
        self.assertEqual(blocked.status_code, 429)

    def test_normal_rate_does_not_block_a_handful_of_requests(self):
        User.objects.create_user(email="marko@pausalac.rs", password="s3cr3t-pass")
        url = reverse("auth-login", kwargs={"version": "v1"})
        response = self.client.post(
            url,
            {"email": "marko@pausalac.rs", "password": "s3cr3t-pass"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
