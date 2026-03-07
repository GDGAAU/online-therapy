"""
account/tokens.py
==================
Opaque token utilities.

Pattern:
  1. Generate a cryptographically random raw token.
  2. SHA-256 hash it and store only the hash in the DB.
  3. Email the raw token to the user.
  4. On submission: hash the received raw token, compare with DB hash.

This means even if the DB is compromised, tokens cannot be reused.
"""

import hashlib
import secrets
from datetime import timedelta
from django.utils import timezone


def generate_opaque_token() -> tuple[str, str]:
    """
    Returns (raw_token, hashed_token).
    Store hashed_token in DB; send raw_token to user.
    """
    raw_token = secrets.token_urlsafe(40)
    hashed_token = hash_token(raw_token)
    return raw_token, hashed_token


def hash_token(raw_token: str) -> str:
    """SHA-256 hash a raw token for safe DB storage."""
    return hashlib.sha256(raw_token.encode()).hexdigest()


def activation_expiry() -> timezone.datetime:
    """Activation tokens expire in 24 hours."""
    return timezone.now() + timedelta(hours=24)


def password_reset_expiry() -> timezone.datetime:
    """Password reset tokens expire in 1 hour."""
    return timezone.now() + timedelta(hours=1)
