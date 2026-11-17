from alembic import context
from app.core.config import ensure_storage
from app.db.session import engine
from app.db.models import Base

target_metadata = Base.metadata


def run_migrations_online():
    ensure_storage()
    with engine.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    raise RuntimeError("Use online migrations against MySQL.")
run_migrations_online()
