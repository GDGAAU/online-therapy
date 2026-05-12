"""Development Settings"""
from .base import *  # noqa: F401, F403
import os

DEBUG = True

# Use console backend when SendGrid is not configured in development.
EMAIL_BACKEND = (
    "anymail.backends.sendgrid.EmailBackend"
    if os.environ.get("SENDGRID_API_KEY")
    else "django.core.mail.backends.console.EmailBackend"
)

# Django Debug Toolbar (optional but useful)
INSTALLED_APPS += ["django_extensions"]  # noqa: F405

# Disable throttling in dev
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []  # noqa: F405

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
    "loggers": {
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG",  # Shows SQL queries
            "propagate": False,
        },
    },
}
