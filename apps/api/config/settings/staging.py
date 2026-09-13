"""Staging settings — production-like, but explicitly not production."""

from .base import *  # Django multi-settings pattern (see pyproject.toml per-file-ignores)

DEBUG = False

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# TODO(deploy): once app.* and api.* share a parent domain, set
# SESSION_COOKIE_DOMAIN / CSRF_COOKIE_DOMAIN to ".pausalac.rs" (or the
# real staging domain) so the session cookie is readable across subdomains.

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
