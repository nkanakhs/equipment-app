"""Explicit management commands; importing the application never changes its schema."""

import argparse
from alembic import command
from alembic.config import Config
from app.core.config import PROJECT_DIR, ensure_storage


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["upgrade", "check"])
    args = parser.parse_args()
    ensure_storage()
    config = Config(str(PROJECT_DIR / "alembic.ini"))
    if args.command == "upgrade":
        command.upgrade(config, "head")
    else:
        from sqlalchemy import text
        from app.db.session import engine

        with engine.connect() as connection:
            result = "ok" if connection.execute(text("SELECT 1")).scalar_one() == 1 else "failed"
            revision = connection.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar_one()
            from app.db.migrations import expected_revision

            if result != "ok" or revision != expected_revision():
                raise SystemExit(f"Database check failed: {result}; revision={revision}")
            print(f"MySQL connection: {result}; revision: {revision}")


if __name__ == "__main__":
    main()
