from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import requests


def fetch_lab_result(lab_url: str, *, timeout: float = 30.0) -> Any:
    """GET ``lab_url`` and return the parsed JSON body (dict or list).

    Only ``http`` and ``https`` URLs are allowed. Non-2xx responses raise
    ``requests.HTTPError``; invalid JSON raises ``requests.JSONDecodeError``.
    """
    parsed = urlparse(lab_url)
    if parsed.scheme not in ("http", "https"):
        msg = "lab_url must use http or https"
        raise ValueError(msg)

    response = requests.get(lab_url, timeout=timeout)
    response.raise_for_status()
    return response.json()
