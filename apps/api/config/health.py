"""Health/readiness endpoint.

Deliberately lightweight and dependency-free at this stage (master prompt
§68: "/health and appropriate readiness checks"). As domains that depend on
external services (storage, Celery broker, integrations) come online, this
should grow into a proper readiness check that verifies those connections
rather than just process liveness.
"""

from django.http import JsonResponse


def health(request):
    return JsonResponse({"status": "ok"})
