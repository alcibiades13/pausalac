from django.db import migrations

# Prices are round figures inside the ranges master prompt §50 /
# blueprint §12 give — both documents state explicitly these are
# approximate, not final ("Exact pricing is not final"). Editable via
# /admin/ without a deploy; the frontend never hardcodes them (§50: "Do
# not hard-code prices into frontend"). See docs/decisions-log.md.
PLANS = [
    {
        "identifier": "starter",
        "name": "Starter",
        "price": "1500.00",
    },
    {
        "identifier": "professional",
        "name": "Professional",
        "price": "2000.00",
    },
    {
        "identifier": "business",
        "name": "Business",
        "price": "3000.00",
    },
]


def seed_plans(apps, schema_editor):
    Plan = apps.get_model("subscriptions", "Plan")
    for plan in PLANS:
        Plan.objects.create(
            identifier=plan["identifier"],
            name=plan["name"],
            price=plan["price"],
            currency="RSD",
            billing_interval="monthly",
            entitlements={},
        )


def unseed_plans(apps, schema_editor):
    Plan = apps.get_model("subscriptions", "Plan")
    Plan.objects.filter(identifier__in=[plan["identifier"] for plan in PLANS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("subscriptions", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_plans, unseed_plans),
    ]
