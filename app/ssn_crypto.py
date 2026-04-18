from __future__ import annotations

import base64
import hashlib
import re
from typing import Final

from cryptography.fernet import Fernet, InvalidToken

# Application-specific domain separation for key derivation (not a secret).
_KDF_CONTEXT: Final[bytes] = b"flask-health-clinic-patient-ssn-v1"

_DIGITS_ONLY = re.compile(r"\D")


def _fernet_from_key(key: str | bytes) -> Fernet:
    material = key.encode("utf-8") if isinstance(key, str) else key
    if not material:
        msg = "encryption key must not be empty"
        raise ValueError(msg)
    digest = hashlib.sha256(_KDF_CONTEXT + material).digest()
    fernet_key = base64.urlsafe_b64encode(digest)
    return Fernet(fernet_key)


def _normalize_ssn(ssn: str) -> str:
    digits = _DIGITS_ONLY.sub("", ssn)
    if len(digits) != 9:
        msg = "SSN must contain exactly 9 digits"
        raise ValueError(msg)
    return digits


def encrypt_ssn(ssn: str, key: str | bytes) -> str:
    """Encrypt a patient SSN for database storage (returns ASCII-safe text).

    ``key`` should be a long random secret from your KMS or environment (same value
    used later in ``decrypt_ssn``). The SSN may include separators; only digits are kept.
    """
    normalized = _normalize_ssn(ssn)
    f = _fernet_from_key(key)
    token = f.encrypt(normalized.encode("ascii"))
    return token.decode("ascii")


def decrypt_ssn(ciphertext: str, key: str | bytes) -> str:
    """Decrypt a value produced by ``encrypt_ssn``; returns nine digits (no separators)."""
    f = _fernet_from_key(key)
    try:
        plain = f.decrypt(ciphertext.encode("ascii"))
    except InvalidToken as exc:
        msg = "invalid ciphertext or wrong key"
        raise ValueError(msg) from exc
    s = plain.decode("ascii")
    return _normalize_ssn(s)
