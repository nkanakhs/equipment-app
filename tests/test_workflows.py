import ast
import json
import io
import re
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from sqlalchemy import select

from app.core.config import PROJECT_DIR
from app.db.models import Equipment
from app.db.session import engine
from app.main import app


def scalar(sql, parameters=()):
    with engine.connect() as connection:
        return connection.exec_driver_sql(sql.replace('?', '%s'), parameters).scalar_one()


def test_health_and_login_without_setup(anonymous):
    assert anonymous.get("/healthz").json() == {"status": "ok"}
    assert anonymous.get("/").headers["location"].startswith("/login")
    assert anonymous.get("/login").status_code == 200
    assert "/setup" not in app.openapi()["paths"]


def test_default_admin_migration_and_repeated_upgrade(anonymous):
    from alembic import command
    from alembic.config import Config
    from alembic.migration import MigrationContext
    from alembic.operations import Operations
    from app.core.security import hash_password
    from sqlalchemy import text
    import importlib.util

    path = PROJECT_DIR / "migrations/versions/0002_default_admin.py"
    spec = importlib.util.spec_from_file_location("default_admin_migration", path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    with engine.begin() as connection:
        with Operations.context(MigrationContext.configure(connection)):
            migration.upgrade()
    assert anonymous.post("/login", data={
        "username": "admin", "password": "QWErty123!@#"
    }).status_code == 303
    changed_hash = hash_password("changed-password-123")
    with engine.begin() as connection:
        connection.execute(text("UPDATE users SET password_hash=:hash WHERE username='admin'"),
                           {"hash": changed_hash})
        with Operations.context(MigrationContext.configure(connection)):
            migration.upgrade()
    command.upgrade(Config(str(PROJECT_DIR / "alembic.ini")), "head")
    with engine.connect() as connection:
        assert connection.execute(text("SELECT password_hash FROM users WHERE username='admin'")).scalar_one() == changed_hash


def test_station_codes_allow_empty_but_reject_duplicates():
    from sqlalchemy.exc import IntegrityError
    from app.db.models import MissionDestinations

    table = MissionDestinations.__table__
    with engine.begin() as connection:
        connection.execute(table.insert(), [
            {"name": "Station A", "station_code": ""},
            {"name": "Station B", "station_code": ""},
            {"name": "Station C", "station_code": "ST-001"},
        ])
    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(table.insert(), {"name": "Station D", "station_code": "ST-001"})


def test_login_logout_and_invalid_password(admin):
    assert admin.post("/logout").status_code == 303
    assert admin.get("/").headers["location"].startswith("/login")
    assert (
        admin.post("/login", data={"username": "test-admin", "password": "wrong"}).status_code
        == 401
    )
    response = admin.post(
        "/login", data={"username": "TEST-ADMIN", "password": "test-password-123"}
    )
    assert response.status_code == 303
    assert "HttpOnly" in response.headers["set-cookie"]
    assert admin.get("/").status_code == 200


@pytest.mark.parametrize(
    "path",
    [
        "/",
        "/equipment",
        "/equipment/new",
        "/categories",
        "/teams",
        "/locations",
        "/settings",
        "/checkout-return",
        "/history/missions",
        "/history/individual",
        "/picking-lists",
        "/account",
    ],
)
def test_pages_render(admin, path):
    response = admin.get(path)
    assert response.status_code == 200, response.text
    assert "text/html" in response.headers["content-type"]


def test_equipment_details_search_and_sql_injection(admin, equipment):
    assert admin.get(f"/equipment/{equipment}").status_code == 200
    assert admin.get(f"/equipment/{equipment}/edit").status_code == 200
    assert admin.get(f"/api/equipment/{equipment}").status_code == 200
    response = admin.get("/equipment", params={"q": "TEST-001"})
    assert response.status_code == 200 and "TEST-001" in response.text
    assert admin.get("/equipment", params={"q": "' OR 1=1 --"}).status_code == 200
    with engine.connect() as connection:
        assert connection.execute(select(Equipment.code)).scalar_one() == "TEST-001"


def test_user_permissions(admin, equipment):
    result = admin.post(
        "/settings/users/new",
        data={
            "username": "test-user",
            "full_name": "Test User",
            "role": "USER",
            "password": "user-password-123",
        },
    )
    assert result.status_code == 303
    admin.post("/logout")
    assert (
        admin.post(
            "/login", data={"username": "test-user", "password": "user-password-123"}
        ).status_code
        == 303
    )
    assert admin.get("/equipment").status_code == 200
    assert admin.get("/settings").status_code == 403
    assert (
        admin.post("/equipment/new", data={"code": "BLOCKED", "description": "Blocked"}).status_code
        == 403
    )
    assert admin.post("/categories/new", data={"name": "Blocked"}).status_code == 403
    assert admin.post("/picking-lists/new", data={"title": "Allowed planning"}).status_code == 303
    assert scalar("SELECT COUNT(*) FROM equipment") == 1


def test_individual_checkout_and_return(admin, equipment):
    result = admin.post(
        f"/equipment/{equipment}/checkout",
        data={
            "borrower_name": "Tester",
            "checkout_date": "2026-10-29",
        },
    )
    assert result.status_code == 303, result.text
    assert scalar("SELECT status FROM equipment WHERE id=?", (equipment,)) == "Σε Χρήση"
    loan_id = scalar("SELECT id FROM loans WHERE equipment_id=?", (equipment,))
    assert (
        admin.post(f"/loans/{loan_id}/return", data={"return_date": "2026-10-29"}).status_code
        == 303
    )
    assert scalar("SELECT active FROM loans WHERE id=?", (loan_id,)) == 0
    assert scalar("SELECT status FROM equipment WHERE id=?", (equipment,)) == "Διαθέσιμο"


def test_concurrent_checkout_is_not_duplicated(admin, equipment):
    def checkout(_):
        return admin.post(
            f"/equipment/{equipment}/checkout",
            data={
                "borrower_name": "Concurrent tester",
                "checkout_date": "2026-10-29",
            },
        ).status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        statuses = list(executor.map(checkout, range(2)))
    assert sorted(statuses) == [303, 400]
    assert scalar("SELECT COUNT(*) FROM loans WHERE active=1") == 1


def test_failed_checkout_rolls_back(admin, equipment, monkeypatch):
    from fastapi import HTTPException
    from app.repositories import equipment as queries

    def fail_after_insert(*args):
        raise HTTPException(status_code=500, detail="Injected failure")

    monkeypatch.setattr(queries, "checkout_equipment_3", fail_after_insert)
    response = admin.post(
        f"/equipment/{equipment}/checkout",
        data={
            "borrower_name": "Rollback tester",
            "checkout_date": "2026-10-29",
        },
    )
    assert response.status_code == 500
    assert scalar("SELECT COUNT(*) FROM loans") == 0
    assert scalar("SELECT status FROM equipment WHERE id=?", (equipment,)) == "Διαθέσιμο"


def test_mission_start_and_return(admin, equipment):
    result = admin.post(
        "/missions/new",
        data={
            "destination": "Test station",
            "team_name": "Test team",
            "departure_date": "2026-10-29",
        },
    )
    assert result.status_code == 303
    mission_id = scalar("SELECT id FROM field_missions")
    assert (
        admin.post(
            f"/missions/{mission_id}/items/add", data={"equipment_id": equipment}
        ).status_code
        == 303
    )
    assert admin.get(f"/missions/{mission_id}").status_code == 200
    assert admin.post(f"/missions/{mission_id}/start").status_code == 303
    assert scalar("SELECT status FROM equipment WHERE id=?", (equipment,)) == "Σε Αποστολή"
    assert (
        admin.post(
            f"/missions/{mission_id}/return-all", data={"return_date": "2026-10-29"}
        ).status_code
        == 303
    )
    assert scalar("SELECT status FROM equipment WHERE id=?", (equipment,)) == "Διαθέσιμο"


def test_picking_list_duplicate_and_checkout(admin, equipment):
    assert admin.post("/picking-lists/new", data={"title": "Test List"}).status_code == 303
    list_id = scalar("SELECT id FROM picking_lists")
    path = f"/api/picking-lists/{list_id}/items/{equipment}"
    assert admin.post(path).status_code == 200
    assert admin.post(path).status_code == 409
    assert admin.get("/picking-lists", params={"list_id": list_id, "q": "TEST"}).status_code == 200
    result = admin.post(
        f"/picking-lists/{list_id}/checkout",
        data={"borrower_name": "Tester", "checkout_date": "2026-10-29"},
    )
    assert result.status_code == 303
    assert scalar("SELECT active FROM loans") == 1


def test_photo_pdf_and_backup(admin, equipment, tmp_path):
    response = admin.post(
        f"/equipment/{equipment}/documents",
        files={"document": ("manual.pdf", b"%PDF-1.4\n%%EOF", "application/pdf")},
    )
    assert response.status_code == 303, response.text
    backup = admin.get("/settings/backup")
    assert backup.status_code == 200
    with zipfile.ZipFile(io.BytesIO(backup.content)) as archive:
        assert "data/equipment.sql" in archive.namelist()
        assert any(
            name.replace("\\", "/").startswith("uploads/documents/") for name in archive.namelist()
        )
        assert b"CREATE TABLE" in archive.read("data/equipment.sql")


def test_static_assets_are_served(admin):
    for path in ["/", "/equipment", "/settings", "/teams", "/locations"]:
        html = admin.get(path).text
        for asset in re.findall(r'(?:src|href)="(/static/[^"?]+)', html):
            assert admin.get(asset).status_code == 200, asset


def test_no_schema_mutations_on_import():
    source = (PROJECT_DIR / "app/main.py").read_text(encoding="utf-8")
    assert "create_database" not in source
    assert len(source.splitlines()) < 100


def test_original_routes_preserved():
    expected = json.loads((Path(__file__).parent / "route_contract.json").read_text())
    actual = {
        (method.upper(), path)
        for path, operations in app.openapi()["paths"].items()
        for method in operations
    }
    assert all(tuple(route) in actual for route in expected)


def test_sql_is_in_repositories():
    for file in (PROJECT_DIR / "app/services").glob("*.py"):
        tree = ast.parse(file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                assert node.func.attr not in {"execute", "executemany"}, file.name
