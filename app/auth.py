from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import TypeVar

from flask import abort, session

F = TypeVar("F", bound=Callable[..., object])


def clinician_required(view: F) -> F:
    """Require an authenticated clinician (``session['clinician_id']`` set by your login flow)."""

    @wraps(view)
    def wrapped(*args: object, **kwargs: object) -> object:
        if session.get("clinician_id") is None:
            abort(401)
        return view(*args, **kwargs)

    return wrapped  # type: ignore[return-value]
