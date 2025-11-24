"""
Core module for CLEO backend.
Provides security, configuration, and utility functions.
"""

from .security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    validate_password_strength, 
    decode_access_token,  # ⭐ CORRECTION : decode_access_token (pas decode_token)
)

from .config import settings

__all__ = [
    'verify_password',
    'get_password_hash',
    'create_access_token',
    'create_refresh_token',
    validate_password_strength, 
    'decode_access_token',
    'settings',
]