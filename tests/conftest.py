import os
import tempfile

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient

# Tests never open the delivered database or the original project database.
_temporary_storage = tempfile.TemporaryDirectory(prefix="elm-tests-")
os.environ["ELM_STORAGE_DIR"] = _temporary_storage.name

from app.core.config import PROJECT_DIR, ensure_storage  # noqa: E402
from app.db.session import engine  # noqa: E402
from app.main import app  # noqa: E402

ensure_storage()
assert engine.url.database == "equipment_test", "Tests require a separate equipment_test database"
command.upgrade(Config(str(PROJECT_DIR / "alembic.ini")), "head")


@pytest.fixture(autouse=True)
def clean_database():
    from app.db.models import Base
    with engine.begin() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            if table.name != "app_settings":
                connection.execute(table.delete())
    yield


@pytest.fixture
def anonymous():
    with TestClient(app, follow_redirects=False) as client:
        yield client


@pytest.fixture
def admin(anonymous):
    from datetime import datetime
    from app.core.security import hash_password
    from app.db.models import Users

    with engine.begin() as connection:
        connection.execute(Users.__table__.insert().values(
            username="test-admin", full_name="Test Admin", role="ADMIN", active=1,
            password_hash=hash_password("test-password-123"),
            created_at=datetime.now().isoformat(timespec="seconds"),
        ))
    response = anonymous.post(
        "/login",
        data={
            "full_name": "Test Admin",
            "username": "test-admin",
            "password": "test-password-123",
            "password_confirm": "test-password-123",
        },
    )
    assert response.status_code == 303
    yield anonymous


@pytest.fixture
def equipment(admin):
    response = admin.post(
        "/equipment/new",
        data={
            "code": "TEST-001",
            "description": "Δοκιμή εξοπλισμού",
            "quantity": "1",
        },
    )
    assert response.status_code == 303
    with engine.connect() as connection:
        return connection.exec_driver_sql(
            "SELECT id FROM equipment WHERE code='TEST-001'"
        ).scalar_one()


def pytest_sessionfinish(session, exitstatus):
    engine.dispose()
    _temporary_storage.cleanup()
