from __future__ import annotations

import base64
import pickle
from typing import Any

from flask import current_app
from opensearchpy import OpenSearch
from opensearchpy.exceptions import NotFoundError


def load_clinician_session_from_opensearch(session_id: str) -> Any:
    """Load a clinician session document from OpenSearch and unpickle its payload.

    Expects a document whose ``_source`` includes a field ``pickle_b64``: a
    base64-encoded ``pickle`` blob (so it can live inside JSON in OpenSearch).

    Requires a Flask application context with ``opensearch`` initialized.

    .. warning::

        ``pickle`` must only be used on data you fully trust (same as the writer
        of the session). Loading attacker-controlled bytes can execute arbitrary code.
    """
    client: OpenSearch | None = current_app.extensions.get("opensearch")
    if client is None:
        msg = "OpenSearch client is not available"
        raise RuntimeError(msg)

    index = current_app.config.get("OPENSEARCH_CLINICIAN_SESSION_INDEX", "clinician_sessions")

    try:
        doc = client.get(index=index, id=session_id)
    except NotFoundError as exc:
        raise KeyError(session_id) from exc

    source = doc.get("_source") or {}
    encoded = source.get("pickle_b64")
    if not isinstance(encoded, str):
        msg = "_source.pickle_b64 must be a base64-encoded string"
        raise ValueError(msg)

    raw = base64.standard_b64decode(encoded)
    return pickle.loads(raw)
