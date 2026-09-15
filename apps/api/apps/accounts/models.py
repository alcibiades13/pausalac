"""
Custom user model (master prompt §49): email is the unique identifier,
no separate username. Company-scoped roles live on `Membership`
(apps.companies), not here — `is_staff`/`is_superuser` only gate the
Django admin (System Admin, §67).
"""

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email: str, password: str | None, **extra_fields):
        if not email:
            raise ValueError("Email adresa je obavezna.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser mora imati is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser mora imati is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("email adresa", unique=True)
    first_name = models.CharField("ime", max_length=150, blank=True)
    last_name = models.CharField("prezime", max_length=150, blank=True)
    is_active = models.BooleanField("aktivan", default=True)
    is_staff = models.BooleanField("staff status", default=False)
    date_joined = models.DateTimeField("datum registracije", default=timezone.now)
    email_verified_at = models.DateTimeField(null=True, blank=True)

    class Language(models.TextChoices):
        SR = "sr", "srpski"
        EN = "en", "English"
        RU = "ru", "русский"

    language = models.CharField(
        "jezik", max_length=2, choices=Language.choices, default=Language.SR
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        verbose_name = "korisnik"
        verbose_name_plural = "korisnici"

    def __str__(self) -> str:
        return self.email

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def get_short_name(self) -> str:
        return self.first_name or self.email

    @property
    def is_email_verified(self) -> bool:
        return self.email_verified_at is not None

    def has_company_permission(self, company, codename: str) -> bool:
        """
        True if this user can perform `codename` on `company` — either as a
        System Admin (Django superuser), or via an active company Membership
        whose role grants that permission (apps.accounts.permissions).
        """
        if self.is_superuser:
            return True
        if company is None:
            return False

        from apps.accounts.permissions import ROLE_PERMISSIONS
        from apps.companies.models import Membership

        membership = Membership.objects.filter(
            user=self, company=company, status=Membership.Status.ACTIVE
        ).first()
        if membership is None:
            return False
        return codename in ROLE_PERMISSIONS.get(membership.role, set())
