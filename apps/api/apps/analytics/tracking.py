"""
Product analytics event tracking (master prompt §73). No analytics
provider is named anywhere in either source document, so this is a
wired-but-inactive seam exactly like the Sentry integration
(config/settings/base.py): `track_event` logs structurally today (via
the JSON logging config, greppable/ingestible) and is the single call
site any real provider (PostHog, Plausible, GA, ...) would replace —
callers never need to change when one is actually chosen.
"""

import logging

logger = logging.getLogger("pausalac.analytics")


def track_event(name: str, *, user=None, company=None, **properties) -> None:
    logger.info(
        "product_event",
        extra={
            "event": name,
            "user_id": getattr(user, "id", None),
            "company_id": getattr(company, "id", None),
            **properties,
        },
    )
