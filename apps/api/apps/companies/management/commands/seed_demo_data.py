"""
Dev-only convenience: seeds realistic demo data (clients, invoices across
every status/document type, payments, documents, tax obligations) into an
EXISTING company, for manual exploration of the app. Not part of any real
feature or user flow — never called from anywhere else in the codebase.

Goes entirely through the real service layer (InvoiceService,
PaymentService, DocumentService, TaxService) rather than raw ORM writes,
so every side effect (KPO entries, FinancialEvents, numbering, audit log)
fires exactly as it would for a real user — this is realistic app usage,
not fixture data bypassing the app's own logic.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.clients.models import Client
from apps.companies.models import Company, Membership
from apps.documents.models import Document
from apps.documents.services import DocumentService
from apps.invoices.models import Invoice
from apps.invoices.services import InvoiceService
from apps.payments.services import PaymentService
from apps.taxes.models import TaxObligation
from apps.taxes.services import TaxService

DocumentType = Invoice.DocumentType

CLIENTS = [
    {
        "client_type": "company",
        "name": "Nordic Web Studio d.o.o.",
        "tax_id": "112233445",
        "email": "kontakt@nordicweb.rs",
        "phone": "+381 11 2233 445",
        "address": "Bulevar Zorana Đinđića 12, Beograd",
    },
    {
        "client_type": "company",
        "name": "Petrović Consulting d.o.o.",
        "tax_id": "223344556",
        "email": "office@petrovic-consulting.rs",
        "phone": "+381 21 4455 667",
        "address": "Bulevar Oslobođenja 45, Novi Sad",
    },
    {
        "client_type": "individual",
        "name": "Ana Jovanović",
        "tax_id": "1234567890123",
        "email": "ana.jovanovic@gmail.com",
        "phone": "+381 63 111 2233",
        "address": "Njegoševa 8, Beograd",
    },
    {
        "client_type": "company",
        "name": "TechFlow Solutions d.o.o.",
        "tax_id": "334455667",
        "email": "info@techflow.rs",
        "phone": "+381 11 3344 556",
        "address": "Vojvode Stepe 210, Beograd",
    },
    {
        "client_type": "individual",
        "name": "Marko Nikolić",
        "tax_id": "2345678901234",
        "email": "marko.nikolic@outlook.com",
        "phone": "+381 64 222 3344",
        "address": "Kralja Petra 33, Niš",
    },
    {
        "client_type": "company",
        "name": "GreenLeaf Marketing d.o.o.",
        "tax_id": "445566778",
        "email": "hello@greenleaf.rs",
        "phone": "+381 11 5566 778",
        "address": "Cara Dušana 5, Zemun",
    },
    {
        "client_type": "company",
        "name": "Bakery Deluxe d.o.o.",
        "tax_id": "556677889",
        "email": "narudzbine@bakerydeluxe.rs",
        "phone": "+381 21 6677 889",
        "address": "Zmaj Jovina 22, Novi Sad",
    },
    {
        "client_type": "individual",
        "name": "Jovana Ilić",
        "tax_id": "3456789012345",
        "email": "jovana.ilic@yahoo.com",
        "phone": "+381 65 333 4455",
        "address": "Balkanska 14, Beograd",
    },
    {
        "client_type": "company",
        "name": "Urban Fit Studio d.o.o.",
        "tax_id": "667788990",
        "email": "info@urbanfit.rs",
        "phone": "+381 11 7788 990",
        "address": "Gospodar Jevremova 19, Beograd",
    },
    {
        "client_type": "individual",
        "name": "Stefan Radovanović",
        "tax_id": "4567890123456",
        "email": "stefan.radovanovic@gmail.com",
        "phone": "+381 62 444 5566",
        "address": "Strahinjića Bana 60, Beograd",
    },
]

SERVICES = [
    ("Izrada web sajta", "1", "180000.00"),
    ("SEO optimizacija — mesečni paket", "1", "45000.00"),
    ("Održavanje sistema — mesečni paket", "1", "35000.00"),
    ("Dizajn logotipa i vizuelnog identiteta", "1", "60000.00"),
    ("Konsultacije — UX/UI", "4", "8000.00"),
    ("Mesečni retainer — razvoj", "1", "220000.00"),
    ("Izrada landing stranice", "1", "70000.00"),
    ("Integracija sistema za plaćanje", "1", "95000.00"),
    ("Copywriting — sadržaj za sajt", "6", "6000.00"),
    ("Tehnička podrška", "3", "5000.00"),
]


def _pdf_bytes(title: str) -> bytes:
    from weasyprint import HTML

    return HTML(string=f"<h1>{title}</h1><p>Demo dokument.</p>").write_pdf()


class Command(BaseCommand):
    help = (
        "Seeds ~10 clients and a realistic spread of invoices/payments/"
        "documents/tax obligations into an existing company, for manual UI exploration."
    )

    def add_arguments(self, parser):
        parser.add_argument("--company-id", type=int, required=True)

    def handle(self, *args, **options):
        try:
            company = Company.objects.get(id=options["company_id"])
        except Company.DoesNotExist as exc:
            raise CommandError(f"No company with id={options['company_id']}") from exc

        owner_membership = (
            Membership.objects.filter(company=company, role=Membership.Role.OWNER)
            .select_related("user")
            .first()
        )
        if owner_membership is None:
            raise CommandError(f"Company {company} has no OWNER membership to act as.")
        actor = owner_membership.user

        self.stdout.write(f"Seeding demo data into {company} (actor: {actor.email})...")

        clients = self._seed_clients(company)
        self._seed_invoices(company, clients, actor)
        self._seed_documents(company, actor)
        self._seed_tax_obligations(company, actor)

        overdue_invoices = InvoiceService.mark_overdue_all()
        overdue_taxes = TaxService.mark_overdue_all()

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. {len(clients)} clients, invoices seeded, "
                f"{overdue_invoices} invoice(s) swept to overdue, "
                f"{overdue_taxes} tax obligation(s) swept to overdue."
            )
        )

    def _seed_clients(self, company) -> list[Client]:
        clients = []
        for data in CLIENTS:
            client, created = Client.objects.get_or_create(
                company=company, name=data["name"], defaults=data
            )
            clients.append(client)
            self.stdout.write(f"  client: {client.name} ({'new' if created else 'existing'})")
        return clients

    def _create_invoice(self, company, client, document_type, *, issue_date, due_date, item_index):
        description, quantity, unit_price = SERVICES[item_index % len(SERVICES)]
        return InvoiceService.create_draft(
            company=company,
            client=client,
            line_items=[
                {"description": description, "quantity": quantity, "unit_price": unit_price}
            ],
            document_type=document_type,
            issue_date=issue_date,
            due_date=due_date,
            service_date=issue_date,
            notes="",
        )

    def _seed_invoices(self, company, clients, actor):
        today = timezone.now().date()

        def days_ago(n: int) -> date:
            return today - timedelta(days=n)

        i = 0  # cycles through clients/services

        def next_client() -> Client:
            nonlocal i
            c = clients[i % len(clients)]
            i += 1
            return c

        # 2 drafts — never issued.
        for _ in range(2):
            issue = days_ago(5)
            self._create_invoice(
                company,
                next_client(),
                DocumentType.INVOICE,
                issue_date=issue,
                due_date=issue + timedelta(days=15),
                item_index=i,
            )

        # 2 issued, not sent.
        for _ in range(2):
            issue = days_ago(20)
            inv = self._create_invoice(
                company,
                next_client(),
                DocumentType.INVOICE,
                issue_date=issue,
                due_date=issue + timedelta(days=15),
                item_index=i,
            )
            InvoiceService.issue(inv, actor=actor)

        # 2 issued + sent (marked sent directly — no real email dispatch here).
        for _ in range(2):
            issue = days_ago(30)
            inv = self._create_invoice(
                company,
                next_client(),
                DocumentType.INVOICE,
                issue_date=issue,
                due_date=issue + timedelta(days=15),
                item_index=i,
            )
            InvoiceService.issue(inv, actor=actor)
            InvoiceService.mark_sent(inv, actor=actor)

        # 2 fully paid.
        for _ in range(2):
            issue = days_ago(40)
            inv = self._create_invoice(
                company,
                next_client(),
                DocumentType.INVOICE,
                issue_date=issue,
                due_date=issue + timedelta(days=15),
                item_index=i,
            )
            InvoiceService.issue(inv, actor=actor)
            InvoiceService.mark_sent(inv, actor=actor)
            PaymentService.record_payment(
                inv,
                amount=inv.total,
                paid_at=issue + timedelta(days=10),
                method="bank_transfer",
                notes="",
                actor=actor,
            )

        # 1 partially paid.
        issue = days_ago(25)
        inv = self._create_invoice(
            company,
            next_client(),
            DocumentType.INVOICE,
            issue_date=issue,
            due_date=issue + timedelta(days=15),
            item_index=i,
        )
        InvoiceService.issue(inv, actor=actor)
        InvoiceService.mark_sent(inv, actor=actor)
        PaymentService.record_payment(
            inv,
            amount=(inv.total / 2).quantize(Decimal("0.01")),
            paid_at=issue + timedelta(days=8),
            method="bank_transfer",
            notes="Prva rata",
            actor=actor,
        )

        # 1 overdue — issued/sent, due date already in the past, never paid.
        # mark_overdue_all() (called at the end of handle()) flips this.
        issue = days_ago(45)
        inv = self._create_invoice(
            company,
            next_client(),
            DocumentType.INVOICE,
            issue_date=issue,
            due_date=issue + timedelta(days=15),
            item_index=i,
        )
        InvoiceService.issue(inv, actor=actor)
        InvoiceService.mark_sent(inv, actor=actor)

        # 1 cancelled.
        issue = days_ago(15)
        inv = self._create_invoice(
            company,
            next_client(),
            DocumentType.INVOICE,
            issue_date=issue,
            due_date=issue + timedelta(days=15),
            item_index=i,
        )
        InvoiceService.issue(inv, actor=actor)
        InvoiceService.cancel(inv, actor=actor)

        # 2 Profaktura — one left as-is, one converted into a real invoice.
        issue = days_ago(10)
        pro1 = self._create_invoice(
            company,
            next_client(),
            DocumentType.PROFORMA,
            issue_date=issue,
            due_date=issue + timedelta(days=15),
            item_index=i,
        )
        InvoiceService.issue(pro1, actor=actor)

        issue = days_ago(35)
        pro2 = self._create_invoice(
            company,
            next_client(),
            DocumentType.PROFORMA,
            issue_date=issue,
            due_date=issue + timedelta(days=15),
            item_index=i,
        )
        InvoiceService.issue(pro2, actor=actor)
        converted = InvoiceService.convert_to_invoice(pro2, actor=actor)
        InvoiceService.issue(converted, actor=actor)

        # 1 Avans, issued and fully paid — behaves exactly like a real
        # invoice for KPO/turnover purposes (Phase 6c).
        issue = days_ago(18)
        avans = self._create_invoice(
            company,
            next_client(),
            DocumentType.ADVANCE,
            issue_date=issue,
            due_date=issue + timedelta(days=15),
            item_index=i,
        )
        InvoiceService.issue(avans, actor=actor)
        PaymentService.record_payment(
            avans,
            amount=avans.total,
            paid_at=issue + timedelta(days=2),
            method="bank_transfer",
            notes="Avansna uplata",
            actor=actor,
        )

        self.stdout.write(
            f"  invoices: {Invoice.objects.filter(company=company).count()} total for company"
        )

    def _seed_documents(self, company, actor):
        specs = [
            (Document.Category.CONTRACT, "Ugovor o pružanju usluga — Nordic Web Studio"),
            (Document.Category.TAX_RESOLUTION, "Poresko rešenje 2026"),
            (Document.Category.OTHER, "Beleške sa sastanka — GreenLeaf Marketing"),
        ]
        for category, title in specs:
            if Document.objects.filter(company=company, title=title).exists():
                continue
            file_obj = SimpleUploadedFile(
                f"{title[:40]}.pdf", _pdf_bytes(title), content_type="application/pdf"
            )
            DocumentService.upload(
                company,
                uploaded_by=actor,
                category=category,
                title=title,
                description="",
                file_obj=file_obj,
            )
            self.stdout.write(f"  document: {title}")

    def _seed_tax_obligations(self, company, actor):
        today = timezone.now().date()
        if TaxObligation.objects.filter(company=company).exists():
            self.stdout.write("  tax obligations: already present, skipping resolution creation")
            return

        start = date(today.year, 1, 1)
        end = date(today.year, 12, 1)
        resolution = TaxService.create_resolution(
            company,
            effective_from=start,
            effective_until=end,
            tax_base=Decimal("100000.00"),
            income_tax_amount=Decimal("3000.00"),
            pio_amount=Decimal("6000.00"),
            health_amount=Decimal("4000.00"),
            unemployment_amount=Decimal("500.00"),
            notes="Demo poresko rešenje za 2026.",
        )
        # Mark all but the most recent past month as paid, for realism —
        # the most recent one stays pending/overdue, so the Obaveze page
        # has something to actually show attention on.
        past_obligations = list(
            resolution.obligations.filter(due_date__lt=today).order_by("period_start")
        )
        for obligation in past_obligations[:-1]:
            TaxService.mark_paid(obligation, actor=actor)
        self.stdout.write(
            f"  tax obligations: {resolution.obligations.count()} generated for {today.year}"
        )
