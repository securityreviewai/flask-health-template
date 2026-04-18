from __future__ import annotations

from typing import Any, Mapping
from urllib.parse import urlparse

import requests
from flask import current_app


def post_pharmacy_prescription_webhook(
    payload: Mapping[str, Any],
    *,
    timeout: float = 30.0,
) -> requests.Response:
    """POST ``payload`` as JSON to the pharmacy webhook URL from app config.

    Reads ``PHARMACY_CALLBACK_URL`` from ``current_app.config``. Must run inside an
    application context. Returns the :class:`requests.Response` (caller may inspect
    status, body, headers).
    """
    callback_url = (current_app.config.get("PHARMACY_CALLBACK_URL") or "").strip()
    if not callback_url:
        msg = "PHARMACY_CALLBACK_URL is not set in application config"
        raise RuntimeError(msg)

    parsed = urlparse(callback_url)
    if parsed.scheme not in ("http", "https"):
        msg = "PHARMACY_CALLBACK_URL must use http or https"
        raise ValueError(msg)

    return requests.post(
        callback_url,
        json=payload,
        timeout=timeout,
        headers={"Accept": "application/json"},
    )
