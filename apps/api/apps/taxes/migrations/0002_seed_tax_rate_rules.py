from django.db import migrations

SOURCE = (
    "2026-09-14 consultation, see docs/decisions-log.md — pending confirmation "
    "against a primary legal source (Zakon o doprinosima za obavezno socijalno "
    "osiguranje / Zakon o porezu na dohodak građana)."
)

RATES = [
    {"identifier": "income_tax_rate", "config": {"rate": "0.1000"}},
    {"identifier": "pio_rate", "config": {"rate": "0.2400"}},
    {"identifier": "health_rate", "config": {"rate": "0.1030"}},
    {"identifier": "unemployment_rate", "config": {"rate": "0.0075"}},
]


def seed_rates(apps, schema_editor):
    RegulatoryRule = apps.get_model("limits", "RegulatoryRule")
    for rate in RATES:
        RegulatoryRule.objects.create(
            identifier=rate["identifier"],
            config=rate["config"],
            effective_from="2026-01-01",
            source=SOURCE,
            version=1,
            approval_status="unverified",
        )


def unseed_rates(apps, schema_editor):
    RegulatoryRule = apps.get_model("limits", "RegulatoryRule")
    RegulatoryRule.objects.filter(
        identifier__in=[rate["identifier"] for rate in RATES], version=1
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("taxes", "0001_initial"),
        ("limits", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_rates, unseed_rates),
    ]
