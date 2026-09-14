"""
Base Django settings shared by every environment.

Environment-specific overrides live in dev.py / staging.py / production.py.
Nothing environment-specific (debug flags, hosts, secrets) belongs here.
"""

from pathlib import Path

import environ
from corsheaders.defaults import default_headers

# apps/api/config/settings/base.py -> apps/api/
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
# Look for a .env file at the repo root (two levels above apps/api).
environ.Env.read_env(BASE_DIR.parent.parent / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY", default="django-insecure-local-dev-only")

DEBUG = False
ALLOWED_HOSTS: list[str] = []

# --- Applications ---------------------------------------------------------

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "corsheaders",
    "django_filters",
]

# One Django app per business domain (master prompt §44).
# `sef`, `fiscalization`, `banking`, `ai` are intentionally NOT listed yet —
# they are later-phase integration seams, not implemented domains.
DOMAIN_APPS = [
    "apps.accounts",
    "apps.companies",
    "apps.clients",
    "apps.invoices",
    "apps.payments",
    "apps.kpo",
    "apps.limits",
    "apps.taxes",
    "apps.documents",
    "apps.notifications",
    "apps.analytics",
    "apps.accounting",
    "apps.subscriptions",
    "apps.integrations",
    "apps.audit",
    "apps.admin_panel",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + DOMAIN_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.audit.context.AuditContextMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# --- Database --------------------------------------------------------------
# PostgreSQL only (master prompt §46) — no sqlite fallback, so financial
# Decimal/NUMERIC behavior matches production from day one.

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=(
            f"postgres://{env('POSTGRES_USER', default='pausalac')}:"
            f"{env('POSTGRES_PASSWORD', default='pausalac')}@"
            f"{env('POSTGRES_HOST', default='localhost')}:"
            f"{env('POSTGRES_PORT', default='5432')}/"
            f"{env('POSTGRES_DB', default='pausalac')}"
        ),
    )
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom user model (email-based, master prompt §49) — must be set before
# the first migration exists anywhere in the project.
AUTH_USER_MODEL = "accounts.User"

# --- Password validation ----------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Internationalization ---------------------------------------------------
# Primary product language is Serbian Latin (master prompt §83); code/DB
# identifiers stay English. Django's own admin/locale strings can still use
# Django's built-in translations.

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Belgrade"
USE_I18N = True
USE_TZ = True

# --- Static & media files ---------------------------------------------------

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# --- Django REST Framework --------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "config.pagination.DefaultPagination",
    "PAGE_SIZE": 25,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_VERSION": "v1",
    "ALLOWED_VERSIONS": ["v1"],
    "EXCEPTION_HANDLER": "config.exceptions.api_exception_handler",
    # Rate limiting (master prompt §48) — backed by the already-running
    # Redis via Django's cache framework (CACHES["default"], set below),
    # no new infra. `auth` is a tighter scope applied explicitly to
    # register/login (apps/accounts/views.py) — the actual abuse targets
    # — everything else gets the general per-user/per-IP rate.
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.ScopedRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "auth": "10/min",
        "user": "300/min",
        "anon": "60/min",
    },
}

# ScopedRateThrottle only applies where a view sets `throttle_scope` — views
# without one aren't affected by the "auth" rate above, only by the default
# User/Anon rates.
#
# REDIS_URL (db 0) has been reserved in .env.example since Phase 1a but had
# no real consumer until now — Celery already owns db 1 (CELERY_BROKER_URL
# below); this is the first actual use of the general-purpose Redis slot.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://localhost:6380/0"),
    }
}

# --- CORS --------------------------------------------------------------------
# The SPA (apps/app) and marketing site (apps/web) run on separate origins
# in local dev; environment-specific allow-lists live in dev/staging/prod.

CORS_ALLOWED_ORIGINS: list[str] = []
# The SPA sends the session cookie + CSRF header on every mutating request
# (master prompt §49 "session management" — see docs/decisions-log.md).
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = list(default_headers) + ["x-company-id"]

# --- CSRF --------------------------------------------------------------------

CSRF_TRUSTED_ORIGINS: list[str] = []
# Readable by JS on purpose: the SPA reads this cookie and echoes it back as
# the X-CSRFToken header (standard DRF SessionAuthentication + SPA pattern).
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"

# --- Celery ------------------------------------------------------------------

CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/1")
CELERY_RESULT_BACKEND = env("CELERY_BROKER_URL", default="redis://localhost:6379/1")
CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_TRACK_STARTED = True

# --- Object storage (S3-compatible; MinIO locally) --------------------------
# Documents (master prompt §26) must never live as uncontrolled filesystem
# files — always through object storage, even in local dev.

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default="")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="pausalac-documents")
AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL", default=None)
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = True
AWS_QUERYSTRING_EXPIRE = 300  # signed URLs, not public files (master prompt §103)

# --- Email -------------------------------------------------------------------

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="localhost")
EMAIL_PORT = env.int("EMAIL_PORT", default=1025)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=False)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@pausalac.rs")

# --- Frontend -----------------------------------------------------------------
# Base URL used when building links embedded in emails (verification, password
# reset). Points at the Vue app (apps/app), not the Nuxt marketing site.

FRONTEND_URL = env("FRONTEND_URL", default="http://localhost:5173")

# --- Subscriptions -------------------------------------------------------------
# Trial length is a genuine business decision the spec explicitly leaves
# open (master prompt §50/§104 call pricing/limits "TBD"; trial length is
# the same category) — 14 days is an industry-standard default, not a
# regulatory fact, so it's a single constant to change later, not
# something to block Phase 5 on. See docs/decisions-log.md.
SUBSCRIPTION_TRIAL_DAYS = env.int("SUBSCRIPTION_TRIAL_DAYS", default=14)

# --- Logging (master prompt §68) ------------------------------------------------
# Structured (JSON) output — every line is greppable/ingestible by a log
# aggregator instead of freeform text. Doesn't change *what* gets logged,
# only *how* — existing `logger.warning(...)`/etc. calls throughout the
# codebase (invoices/notifications/subscriptions tasks, audit context) are
# unaffected.


class JsonFormatter:
    """Minimal dependency-free JSON log formatter — the log volume here
    doesn't justify adding python-json-logger as a dependency for what's a
    ~15-line class."""

    def __init__(self):
        import logging

        self._base = logging.Formatter()

    def format(self, record):
        import json
        import logging

        payload = {
            "timestamp": self._base.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self._base.formatException(record.exc_info)
        # Anything passed via `logger.info(..., extra={...})` rides along.
        reserved = set(vars(logging.LogRecord("", 0, "", 0, "", (), None)))
        for key, value in vars(record).items():
            if key not in reserved and key not in payload:
                payload[key] = value
        return json.dumps(payload, default=str)


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {"()": "config.settings.base.JsonFormatter"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "json"},
    },
    # Third-party libraries (WeasyPrint, etc.) default to WARNING so their
    # internal INFO-level chatter doesn't drown out application logs — only
    # `django.*` and the app's own `pausalac.*` namespace (apps/*/tasks.py's
    # existing `logging.getLogger("pausalac.<domain>")` convention) run at
    # LOG_LEVEL.
    "root": {"handlers": ["console"], "level": "WARNING"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "pausalac": {
            "handlers": ["console"],
            "level": env("LOG_LEVEL", default="INFO"),
            "propagate": False,
        },
    },
}

# --- Error tracking (master prompt §48/§68) -------------------------------------
# Wired but inert without a DSN — same "architecture seam, not a fake
# integration" treatment as SEF/fiscalization (Company.uses_sef is a real
# field; the integration behind it isn't). No account is required to run
# this app; set SENTRY_DSN once one exists.
SENTRY_DSN = env("SENTRY_DSN", default="")
if SENTRY_DSN:
    import sentry_sdk

    sentry_sdk.init(dsn=SENTRY_DSN, send_default_pii=False, traces_sample_rate=0.1)
