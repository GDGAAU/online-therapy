"""
Core settings package.

Defaults to development settings. Override with:
  DJANGO_SETTINGS_MODULE=core.settings.production
"""

from .development import *  # noqa: F401, F403
