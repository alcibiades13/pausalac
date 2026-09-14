from django.db import migrations

SOURCE = (
    "2026-09-14 consultation, see docs/decisions-log.md — pending confirmation "
    "against a primary legal source (Zakon o porezu na dohodak građana / "
    "Uredba o paušalnom oporezivanju / Zakon o PDV)."
)

RULES = [
    {
        "identifier": "pausal_turnover_limit",
        "config": {"amount": "6000000.00", "currency": "RSD", "period": "calendar_year"},
        "effective_from": "2026-01-01",
        "effective_until": None,
    },
    {
        "identifier": "vat_registration_threshold",
        "config": {"amount": "8000000.00", "currency": "RSD", "period": "trailing_12_months"},
        "effective_from": "2026-01-01",
        "effective_until": None,
    },
    {
        "identifier": "tax_base_growth_cap",
        # Seeded for shape/completeness only — unused until Phase 3c has
        # poresko rešenje data to compare year-over-year against.
        "config": {"max_increase_percentage": "10.00"},
        "effective_from": "2026-01-01",
        "effective_until": "2027-12-31",
    },
]


def seed_rules(apps, schema_editor):
    RegulatoryRule = apps.get_model("limits", "RegulatoryRule")
    for rule in RULES:
        RegulatoryRule.objects.create(
            identifier=rule["identifier"],
            config=rule["config"],
            effective_from=rule["effective_from"],
            effective_until=rule["effective_until"],
            source=SOURCE,
            version=1,
            approval_status="unverified",
        )


def unseed_rules(apps, schema_editor):
    RegulatoryRule = apps.get_model("limits", "RegulatoryRule")
    RegulatoryRule.objects.filter(
        identifier__in=[rule["identifier"] for rule in RULES], version=1
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("limits", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_rules, unseed_rules),
    ]
