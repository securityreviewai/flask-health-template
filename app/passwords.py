from __future__ import annotations

from werkzeug.security import generate_password_hash


def hash_password(password: str) -> str:
    """Return a salted hash of ``password`` for storing on the user row (e.g. ``users.password_hash``).

    Uses PBKDF2-HMAC-SHA256 via Werkzeug—fast enough for an interactive login while
    resisting offline guessing.     At sign-in, verify with ``werkzeug.security.check_password_hash``::

        from werkzeug.security import check_password_hash

        if check_password_hash(stored_hash, plaintext_password):
            ...
    """
    if not isinstance(password, str):
        msg = "password must be a str"
        raise TypeError(msg)
    if not password:
        msg = "password must not be empty"
        raise ValueError(msg)
    return generate_password_hash(password, method="pbkdf2:sha256")
