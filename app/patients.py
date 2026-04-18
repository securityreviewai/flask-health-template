from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Connection


def search_patients(conn: Connection, name_query: str) -> list[Mapping[str, Any]]:
    """Return all patient rows whose ``full_name`` contains ``name_query`` (case-insensitive).

    ``conn`` is a SQLAlchemy 2.0 connection, for example from ``db.engine.connect()``
    or the connection passed into a raw-SQL block.
    """
    pattern = f"%{name_query}%"
    result = conn.execute(
        text("SELECT * FROM patients WHERE full_name ILIKE :pattern"),
        {"pattern": pattern},
    )
    return list(result.mappings().all())
