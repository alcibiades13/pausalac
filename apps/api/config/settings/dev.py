"""Local development settings."""

from .base import *  # Django multi-settings pattern (see pyproject.toml per-file-ignores)

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # apps/app (Vite dev server)
    "http://localhost:3000",  # apps/web (Nuxt dev server)
]
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
]

# Local dev talks to MinIO over plain HTTP with path-style addressing.
AWS_S3_ADDRESSING_STYLE = "path"
AWS_S3_USE_SSL = False

# Loosen DRF auth for local API exploration via the browsable API.
REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
}
