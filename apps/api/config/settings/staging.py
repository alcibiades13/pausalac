"""Staging settings — production-like, but explicitly not production."""

from .base import *  # Django multi-settings pattern (see pyproject.toml per-file-ignores)

DEBUG = False

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# Cross-subdomain session sharing (marketing site / app / api, once all
# three live under one parent domain — see docs/decisions-log.md) — unset
# by default (Django then scopes the cookie to the exact host, today's
# behavior), set for real once a real domain is registered, e.g.
# SESSION_COOKIE_DOMAIN=.pausalac.rs — never hardcoded here, since no
# domain is confirmed yet.
SESSION_COOKIE_DOMAIN = env("SESSION_COOKIE_DOMAIN", default=None)
CSRF_COOKIE_DOMAIN = env("CSRF_COOKIE_DOMAIN", default=None)

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
