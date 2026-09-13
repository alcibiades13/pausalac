"""
First business-domain model to adopt `TenantScopedManager`
(apps.companies.managers) as its *default* manager — the pattern every
later domain (invoices, payments, ...) should copy.
"""

from django.db import models

from apps.companies.managers import TenantScopedManager
from apps.companies.models import Company


class Client(models.Model):
    class ClientType(models.TextChoices):
        INDIVIDUAL = "individual", "Fizičko lice"
        COMPANY = "company", "Pravno lice"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="clients")
    client_type = models.CharField(
        max_length=20, choices=ClientType.choices, default=ClientType.COMPANY
    )
    name = models.CharField("naziv", max_length=255)
    # Deliberately unvalidated beyond "not required" — no confirmed
    # authoritative PIB/JMBG format rule to encode yet (master prompt §81).
    tax_id = models.CharField("PIB / matični broj", max_length=32, blank=True)
    email = models.EmailField("email", blank=True)
    phone = models.CharField("telefon", max_length=32, blank=True)
    address = models.CharField("adresa", max_length=255, blank=True)
    country = models.CharField("država", max_length=2, default="RS")
    default_currency = models.CharField("podrazumevana valuta", max_length=3, default="RSD")
    notes = models.TextField("napomene", blank=True)
    is_active = models.BooleanField("aktivan", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TenantScopedManager()

    class Meta:
        verbose_name = "klijent"
        verbose_name_plural = "klijenti"
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(name__gt=""), name="client_name_not_blank"
            )
        ]

    def __str__(self) -> str:
        return self.name
