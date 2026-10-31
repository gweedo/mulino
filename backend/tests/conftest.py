"""Root test configuration: ensure env vars are correct before any fixture runs."""

import os


def pytest_configure(config) -> None:  # type: ignore[type-arg]
    db = os.environ.get("DATABASE_URL", "")
    # Ensure asyncpg driver is used for async SQLAlchemy
    if db and not db.startswith("postgresql+asyncpg://"):
        db = db.replace("postgresql://", "postgresql+asyncpg://", 1)
        os.environ["DATABASE_URL"] = db
    # Settings requires SUPABASE_URL; tests never call it (keys are overridden).
    os.environ.setdefault("SUPABASE_URL", "https://test-project.supabase.co")
