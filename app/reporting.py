from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from sqlalchemy import text

from app.extensions import db

# Columns the UI may filter on; only these names are ever interpolated into SQL.
_ALLOWED_VISIT_FILTER_COLUMNS: frozenset[str] = frozenset(
    {
        "id",
        "patient_id",
        "doctor_id",
        "visit_date",
        "department",
        "status",
    }
)


def filter_visits(filters: dict[str, Any]) -> list[Mapping[str, Any]]:
    """Run ``SELECT * FROM visits`` constrained by ``filters`` (column -> exact value).

    Unknown keys are ignored. Keys with value ``None`` are skipped (no constraint).
    Must run inside a Flask application context so ``db.session`` is available.
    """
    if not isinstance(filters, dict):
        msg = "filters must be a dict"
        raise TypeError(msg)

    clauses: list[str] = []
    bind: dict[str, Any] = {}

    for col, val in filters.items():
        if col not in _ALLOWED_VISIT_FILTER_COLUMNS:
            continue
        if val is None:
            continue
        param = f"p_{col}"
        clauses.append(f"{col} = :{param}")
        bind[param] = val

    sql = "SELECT * FROM visits"
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY visit_date DESC NULLS LAST, id"

    result = db.session.execute(text(sql), bind)
    return list(result.mappings().all())
