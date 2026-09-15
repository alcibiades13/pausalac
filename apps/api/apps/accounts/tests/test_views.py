import re

from django.core import mail
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User


def _extract_token(email_body: str) -> str:
    match = re.search(r"token=([^\s&]+)", email_body)
    assert match, f"no token found in email body: {email_body!r}"
    return match.group(1)


class RegisterFlowTests(TestCase):
    def test_register_creates_user_logs_in_and_sends_verification_email(self):
        url = reverse("auth-register", kwargs={"version": "v1"})
        response = self.client.post(
            url,
            {
                "email": "marko@pausalac.rs",
                "password": "correct-horse-battery",
                "first_name": "Marko",
                "last_name": "Marković",
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(email="marko@pausalac.rs").exists())

        # session is already active — no separate login call needed
        me_response = self.client.get(reverse("auth-me", kwargs={"version": "v1"}))
        self.assertEqual(me_response.status_code, 200)
        self.assertEqual(me_response.json()["email"], "marko@pausalac.rs")
        self.assertFalse(me_response.json()["is_email_verified"])

        self.assertEqual(len(mail.outbox), 1)

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user(email="marko@pausalac.rs", password="s3cr3t-pass")
        url = reverse("auth-register", kwargs={"version": "v1"})
        response = self.client.post(
            url, {"email": "marko@pausalac.rs", "password": "correct-horse-battery"}
        )
        self.assertEqual(response.status_code, 400)


class VerifyEmailFlowTests(TestCase):
    def test_verify_email_via_link_from_sent_email(self):
        register_url = reverse("auth-register", kwargs={"version": "v1"})
        self.client.post(
            register_url, {"email": "marko@pausalac.rs", "password": "correct-horse-battery"}
        )
        token = _extract_token(mail.outbox[0].body)

        verify_url = reverse("auth-verify-email", kwargs={"version": "v1"})
        response = self.client.post(verify_url, {"token": token})
        self.assertEqual(response.status_code, 200)

        user = User.objects.get(email="marko@pausalac.rs")
        self.assertTrue(user.is_email_verified)

    def test_invalid_token_is_rejected(self):
        verify_url = reverse("auth-verify-email", kwargs={"version": "v1"})
        response = self.client.post(verify_url, {"token": "garbage"})
        self.assertEqual(response.status_code, 400)


class LoginLogoutFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="marko@pausalac.rs", password="s3cr3t-pass")

    def test_login_with_correct_credentials(self):
        url = reverse("auth-login", kwargs={"version": "v1"})
        response = self.client.post(url, {"email": "marko@pausalac.rs", "password": "s3cr3t-pass"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["email"], "marko@pausalac.rs")

    def test_login_with_wrong_password_is_rejected(self):
        # DRF downgrades AuthenticationFailed (401) to 403 whenever no
        # configured authenticator provides a WWW-Authenticate challenge —
        # true here since SessionAuthentication is the only one configured.
        url = reverse("auth-login", kwargs={"version": "v1"})
        response = self.client.post(url, {"email": "marko@pausalac.rs", "password": "wrong"})
        self.assertEqual(response.status_code, 403)

    def test_me_requires_authentication(self):
        # DRF returns 403 (not 401) for anonymous requests when the only
        # configured authenticator is SessionAuthentication, which has no
        # WWW-Authenticate challenge to issue — this is expected, not a bug.
        response = self.client.get(reverse("auth-me", kwargs={"version": "v1"}))
        self.assertEqual(response.status_code, 403)

    def test_logout_ends_session(self):
        self.client.login(username="marko@pausalac.rs", password="s3cr3t-pass")
        logout_url = reverse("auth-logout", kwargs={"version": "v1"})
        response = self.client.post(logout_url)
        self.assertEqual(response.status_code, 204)

        me_response = self.client.get(reverse("auth-me", kwargs={"version": "v1"}))
        self.assertEqual(me_response.status_code, 403)

    def test_user_can_update_their_own_language(self):
        self.client.login(username="marko@pausalac.rs", password="s3cr3t-pass")
        url = reverse("auth-me", kwargs={"version": "v1"})
        response = self.client.patch(url, {"language": "ru"}, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["language"], "ru")

        self.user.refresh_from_db()
        self.assertEqual(self.user.language, "ru")

    def test_invalid_language_is_rejected(self):
        self.client.login(username="marko@pausalac.rs", password="s3cr3t-pass")
        url = reverse("auth-me", kwargs={"version": "v1"})
        response = self.client.patch(url, {"language": "fr"}, content_type="application/json")
        self.assertEqual(response.status_code, 400)

        self.user.refresh_from_db()
        self.assertEqual(self.user.language, "sr")


class PasswordResetFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="marko@pausalac.rs", password="old-password")

    def test_reset_request_for_unknown_email_still_returns_200_and_sends_nothing(self):
        url = reverse("auth-password-reset", kwargs={"version": "v1"})
        response = self.client.post(url, {"email": "nepostoji@pausalac.rs"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

    def test_full_reset_flow(self):
        request_url = reverse("auth-password-reset", kwargs={"version": "v1"})
        self.client.post(request_url, {"email": "marko@pausalac.rs"})
        self.assertEqual(len(mail.outbox), 1)

        body = mail.outbox[0].body
        uid = re.search(r"uid=([^\s&]+)", body).group(1)
        token = re.search(r"token=([^\s&]+)", body).group(1)

        confirm_url = reverse("auth-password-reset-confirm", kwargs={"version": "v1"})
        response = self.client.post(
            confirm_url, {"uid": uid, "token": token, "new_password": "brand-new-password"}
        )
        self.assertEqual(response.status_code, 200)

        login_url = reverse("auth-login", kwargs={"version": "v1"})
        login_response = self.client.post(
            login_url, {"email": "marko@pausalac.rs", "password": "brand-new-password"}
        )
        self.assertEqual(login_response.status_code, 200)
