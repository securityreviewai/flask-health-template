from __future__ import annotations

import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.engine.url import make_url

# PostgreSQL identifiers: unquoted, conservative allow-list for form input.
_SAFE_DB_NAME = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]{0,62}$")


def dump_postgres_database(
    database_name: str,
    *,
    sqlalchemy_database_uri: str,
    backup_root: Path,
    pg_dump_bin: str = "pg_dump",
) -> Path:
    """Run ``pg_dump -Fc`` for ``database_name`` using host/user/password from ``sqlalchemy_database_uri``.

    Writes under ``backup_root`` (created if missing). Returns the dump file path.
    Raises ``ValueError`` if ``database_name`` is not a safe identifier, and
    ``subprocess.CalledProcessError`` if ``pg_dump`` fails.
    """
    name = database_name.strip()
    if not _SAFE_DB_NAME.fullmatch(name):
        msg = "database_name must be a valid PostgreSQL identifier (letters, digits, underscore)"
        raise ValueError(msg)

    url = make_url(sqlalchemy_database_uri)
    driver = url.drivername or ""
    if not driver.startswith("postgresql"):
        msg = "SQLALCHEMY_DATABASE_URI must be a PostgreSQL URL"
        raise ValueError(msg)

    if not url.host or not url.username:
        msg = "Database URI must include host and username for pg_dump"
        raise ValueError(msg)

    backup_root = backup_root.resolve()
    backup_root.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_file = backup_root / f"{name}_{stamp}.dump"

    port = url.port if url.port is not None else 5432
    env = {**os.environ, "PGPASSWORD": url.password or ""}

    cmd = [
        pg_dump_bin,
        "-h",
        url.host,
        "-p",
        str(port),
        "-U",
        url.username,
        "-Fc",
        "-f",
        str(out_file),
        name,
    ]

    subprocess.run(
        cmd,
        check=True,
        capture_output=True,
        env=env,
        timeout=3600,
    )
    return out_file
