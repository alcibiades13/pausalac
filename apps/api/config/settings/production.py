"""Production settings.

Never point this at production credentials from a local machine
(master prompt §69) — this module only reads from the environment.
"""

from .base import *  # Django multi-settings pattern (see pyproject.toml per-file-ignores)

DEBUG = False

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# TODO(deploy): same cross-subdomain cookie domain note as staging.py —
# resolve once the real production domain is decided (docs/implementation-plan.md).

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
