from django.test import TestCase

from apps.accounts.models import User
from apps.accounts.services import (
    TokenError,
    consume_email_verification_token,
    consume_password_reset_token,
    make_email_verification_token,
    make_password_reset_tokens,
)


class EmailVerificationTokenTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="marko@pausalac.rs", password="s3cr3t-pass")

    def test_valid_token_resolves_to_user(self):
        token = make_email_verification_token(self.user)
        resolved = consume_email_verification_token(token)
        self.assertEqual(resolved.pk, self.user.pk)

    def test_tampered_token_is_rejected(self):
        token = make_email_verification_token(self.user)
        with self.assertRaises(TokenError):
            consume_email_verification_token(token + "tampered")

    def test_garbage_token_is_rejected(self):
        with self.assertRaises(TokenError):
            consume_email_verification_token("not-a-real-token")


class PasswordResetTokenTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="marko@pausalac.rs", password="s3cr3t-pass")

    def test_valid_token_resolves_to_user(self):
        uidb64, token = make_password_reset_tokens(self.user)
        resolved = consume_password_reset_token(uidb64, token)
        self.assertEqual(resolved.pk, self.user.pk)

    def test_token_is_single_use_once_password_changes(self):
        uidb64, token = make_password_reset_tokens(self.user)
        self.user.set_password("brand-new-pass")
        self.user.save()
        with self.assertRaises(TokenError):
            consume_password_reset_token(uidb64, token)

    def test_invalid_uid_is_rejected(self):
        with self.assertRaises(TokenError):
            consume_password_reset_token("not-base64", "irrelevant-token")
