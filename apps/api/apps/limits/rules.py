"""
Rule resolution — the only place that reads RegulatoryRule for a given
date. Raises rather than guessing when no rule matches: a missing rule
for a queried date is a data problem to fix, not something to silently
fall back on (master prompt §81/82 applied to code, not just to product
copy).
"""

from datetime import date

from django.db.models import Q

from apps.limits.models import RegulatoryRule


def get_active_rule(identifier: str, as_of: date) -> RegulatoryRule:
    rule = (
        RegulatoryRule.objects.filter(identifier=identifier, effective_from__lte=as_of)
        .filter(Q(effective_until__isnull=True) | Q(effective_until__gte=as_of))
        .order_by("-effective_from", "-version")
        .first()
    )
    if rule is None:
        raise RegulatoryRule.DoesNotExist(
            f"No active RegulatoryRule for identifier={identifier!r} as_of={as_of!r}"
        )
    return rule
