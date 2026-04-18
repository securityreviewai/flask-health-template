from __future__ import annotations

from datetime import date
from typing import Any

from psycopg2.extensions import connection as PsycopgConnection
from psycopg2.extras import RealDictCursor


def fetch_appointments_for_doctor_date(
    conn: PsycopgConnection,
    doctor_id: int,
    appointment_date: date,
) -> list[dict[str, Any]]:
    """Return every row from ``appointments`` for ``doctor_id`` on the given calendar day.

    ``appointment_date`` is the calendar date of the visit (compared to the date part
    of ``scheduled_at``). Typical Flask usage::

        doctor_id = int(request.args["doctor_id"])
        appointment_date = date.fromisoformat(request.args["appointment_date"])
        rows = fetch_appointments_for_doctor_date(conn, doctor_id, appointment_date)
    """
    sql = """
        SELECT *
        FROM appointments
        WHERE doctor_id = %s
          AND scheduled_at::date = %s
        ORDER BY scheduled_at
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, (doctor_id, appointment_date))
        rows = cur.fetchall()
    return [dict(row) for row in rows]
