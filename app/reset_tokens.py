from __future__ import annotations

import secrets

# 62 symbols → ~47.6 bits of entropy for an 8-character token (suitable for reset links).
_ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def generate_password_reset_token() -> str:
    """Return an 8-character alphanumeric token for clinician password-reset emails.

    Uses :mod:`secrets` (CSPRNG), not :func:`random.random`.
    """
    return "".join(secrets.choice(_ALPHABET) for _ in range(8))
