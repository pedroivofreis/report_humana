#!/usr/bin/env python3
"""Reset database - drops all tables and recreates them.

Usage:
  python scripts/reset_database.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text

from app.db.base import Base
from app.db.session import engine


async def reset_database() -> None:
    """Drop all tables and recreate them."""
    print("🔄 Resetting database...")

    async with engine.begin() as conn:
        # Drop all tables
        print("  ⏳ Dropping all tables...")
        await conn.run_sync(Base.metadata.drop_all)
        print("  ✅ All tables dropped")

        # Create all tables
        print("  ⏳ Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)
        print("  ✅ All tables created")

        # Reset alembic version to head
        print("  ⏳ Setting alembic version...")
        # First, create alembic_version table if it doesn't exist
        await conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS alembic_version (
                version_num VARCHAR(32) NOT NULL,
                CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
            )
        """
            )
        )

        # Delete existing version
        await conn.execute(text("DELETE FROM alembic_version"))

        # Insert current head version (the latest migration)
        await conn.execute(
            text("INSERT INTO alembic_version (version_num) VALUES ('be698ae17eb7')")
        )
        print("  ✅ Alembic version set to head (be698ae17eb7)")

    print("✅ Database reset completed!")


if __name__ == "__main__":
    asyncio.run(reset_database())
