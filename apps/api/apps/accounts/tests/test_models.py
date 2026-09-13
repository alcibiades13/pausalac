from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from apps.accounts.models import User


class UserManagerTests(TestCase):
    def test_create_user_requires_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="s3cr3t-pass")

    def test_create_user_normalizes_email_domain(self):
        user = User.objects.create_user(email="marko@GMAIL.com", password="s3cr3t-pass")
        self.assertEqual(user.email, "marko@gmail.com")
        self.assertTrue(user.check_password("s3cr3t-pass"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser_sets_admin_flags(self):
        admin = User.objects.create_superuser(email="admin@pausalac.rs", password="s3cr3t-pass")
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_create_superuser_rejects_is_staff_false(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="admin@pausalac.rs", password="s3cr3t-pass", is_staff=False
            )

    def test_email_is_unique(self):
        User.objects.create_user(email="dup@pausalac.rs", password="s3cr3t-pass")
        with self.assertRaises((IntegrityError, DjangoValidationError)):
            User.objects.create_user(email="dup@pausalac.rs", password="another-pass")

    def test_is_email_verified_defaults_false(self):
        user = User.objects.create_user(email="marko@pausalac.rs", password="s3cr3t-pass")
        self.assertFalse(user.is_email_verified)
