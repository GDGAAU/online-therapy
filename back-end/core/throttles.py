"""
core/throttles.py
==================
Custom rate limiting throttles for authentication endpoints.
"""

import logging
from rest_framework.throttling import SimpleRateThrottle

logger = logging.getLogger(__name__)


class AuthRateThrottle(SimpleRateThrottle):
    """
    Rate limit for JWT token creation: 5 requests/minute per IP.
    """
    scope = 'auth'

    def get_cache_key(self, request, view):
        return self.get_ident(request)  # IP-based

    def allow_request(self, request, view):
        allowed = super().allow_request(request, view)
        if not allowed:
            logger.warning(
                f"Auth rate limit exceeded for IP {self.get_ident(request)} on {request.path}"
            )
        return allowed


class RegisterRateThrottle(SimpleRateThrottle):
    """
    Rate limit for user registration: 3 requests/hour per IP.
    """
    scope = 'register'

    def get_cache_key(self, request, view):
        return self.get_ident(request)  # IP-based

    def allow_request(self, request, view):
        allowed = super().allow_request(request, view)
        if not allowed:
            logger.warning(
                f"Register rate limit exceeded for IP {self.get_ident(request)} on {request.path}"
            )
        return allowed


class PasswordResetRateThrottle(SimpleRateThrottle):
    """
    Rate limit for password reset: 3 requests/hour per email.
    """
    scope = 'password_reset'

    def get_cache_key(self, request, view):
        email = request.data.get('email')
        if email:
            return f"password_reset:{email.lower().strip()}"
        return None  # If no email, don't throttle

    def allow_request(self, request, view):
        allowed = super().allow_request(request, view)
        if not allowed:
            email = request.data.get('email', 'unknown')
            logger.warning(
                f"Password reset rate limit exceeded for email {email} on {request.path}"
            )
        return allowed