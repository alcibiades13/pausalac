"""Health/readiness endpoints (master prompt §68).

`health` stays liveness-only on purpose — a load balancer/orchestrator
hitting it repeatedly should never touch the DB/Redis/storage. `ready`
is the "can this instance actually serve traffic" check, split out so the
two concerns don't get conflated.
"""

import logging

import redis
from django.conf import settings
from django.core.files.storage import default_storage
from django.db import connection
from django.http import JsonResponse

logger = logging.getLogger("pausalac.health")


def health(request):
    return JsonResponse({"status": "ok"})


def _check_database() -> bool:
    try:
        connection.ensure_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return True
    except Exception:
        logger.warning("readiness check: database unreachable", exc_info=True)
        return False


def _check_redis() -> bool:
    try:
        client = redis.from_url(settings.CELERY_BROKER_URL, socket_connect_timeout=2)
        return bool(client.ping())
    except Exception:
        logger.warning("readiness check: redis unreachable", exc_info=True)
        return False


def _check_storage() -> bool:
    try:
        # A HEAD-style existence check on a key that need not exist — this
        # only proves the storage backend is reachable and credentials are
        # valid, not that any particular object is present.
        default_storage.exists("__readiness_probe__")
        return True
    except Exception:
        logger.warning("readiness check: object storage unreachable", exc_info=True)
        return False


def ready(request):
    checks = {
        "database": _check_database(),
        "redis": _check_redis(),
        "storage": _check_storage(),
    }
    all_ok = all(checks.values())
    body = {"status": "ok" if all_ok else "degraded", "checks": checks}
    return JsonResponse(body, status=200 if all_ok else 503)
