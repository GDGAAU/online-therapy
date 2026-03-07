"""Production Settings"""
from .base import *  # noqa: F401, F403
import sentry_sdk

DEBUG = False

# Sentry for error monitoring
if SENTRY_DSN:  # noqa: F405
    sentry_sdk.init(
        dsn=SENTRY_DSN,  # noqa: F405
        traces_sample_rate=0.1,
        profiles_sample_rate=0.1,
    )

# Security hardening
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}
