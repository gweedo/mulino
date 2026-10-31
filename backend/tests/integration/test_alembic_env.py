"""alembic/env.py must accept any valid DATABASE_URL, including percent-encoded passwords."""

import os
import subprocess
from urllib.parse import urlparse

from pizzeria.infrastructure.settings import get_database_settings


def test_alembic_accepts_percent_encoded_password(_bootstrap_test_db: str) -> None:
    # Supabase passwords often need URL-encoding (@ → %40). configparser treats a bare
    # % as interpolation, so env.py must escape it before handing the URL to Alembic.
    url = urlparse(get_database_settings().DATABASE_URL)
    assert url.password, "test DATABASE_URL needs a password"
    encoded_password = "".join(f"%{ord(c):02X}" for c in url.password)
    netloc = f"{url.username}:{encoded_password}@{url.hostname}:{url.port or 5432}"
    encoded_url = url._replace(netloc=netloc).geturl()

    result = subprocess.run(
        ["alembic", "current"],
        env={**os.environ, "DATABASE_URL": encoded_url},
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
