from __future__ import annotations

import html

from markupsafe import Markup


def soap_notes_to_html(notes: str | None) -> Markup:
    """Turn stored SOAP plain text into HTML safe for embedding, preserving line breaks.

    All markup in the source notes is escaped; only ``<br>`` is inserted for newlines.
    """
    if notes is None:
        return Markup("")
    normalized = notes.replace("\r\n", "\n").replace("\r", "\n")
    escaped = html.escape(normalized, quote=True)
    return Markup(escaped.replace("\n", "<br>\n"))
