"""Application composition only; migrations run separately before startup."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from app.core.config import STATIC_PATH, UPLOADS_PATH, ensure_storage, settings as config
from app.core.authorization import authentication_and_rbac
from app.db.session import ConnectionCleanupMiddleware, engine
from app.db.migrations import expected_revision
from app.routers import (
    auth,
    categories,
    dashboard,
    equipment,
    history,
    locations,
    missions,
    picking_lists,
    settings,
    teams,
)


@asynccontextmanager
async def lifespan(app):
    ensure_storage()
    logging.basicConfig(level=config.log_level.upper())
    with engine.connect() as connection:
        revision = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
        if revision != expected_revision():
            raise RuntimeError("Database schema is not current. Run: python -m app.manage upgrade")
    yield
    engine.dispose()


app = FastAPI(title="Equipment Library Manager", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOADS_PATH, check_dir=False), name="uploads")
app.middleware("http")(authentication_and_rbac)
app.add_middleware(ConnectionCleanupMiddleware)
app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(dashboard.router)
app.include_router(equipment.router)
app.include_router(history.router)
app.include_router(locations.router)
app.include_router(missions.router)
app.include_router(picking_lists.router)
app.include_router(settings.router)
app.include_router(teams.router)


@app.get("/healthz", include_in_schema=False)
def healthz():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"status": "ok"}
