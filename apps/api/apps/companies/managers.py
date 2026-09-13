"""
Tenant-scoping manager mixin (master prompt §47: "never rely only on
frontend filtering for tenant security"). Every future domain model that
belongs to a Company (Client, Invoice, ...) should use this manager so
"forgot to filter by tenant" isn't a per-view mistake to make:

    class Invoice(models.Model):
        company = models.ForeignKey(Company, ...)
        objects = TenantScopedManager()

    Invoice.objects.for_company(request.company)
"""

from django.db import models


class TenantScopedQuerySet(models.QuerySet):
    def for_company(self, company):
        return self.filter(company=company)


class TenantScopedManager(models.Manager.from_queryset(TenantScopedQuerySet)):
    pass
