"""MySQL connections with request-scoped cleanup and serialized write transactions."""

from contextvars import ContextVar
from collections.abc import Mapping
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError as IntegrityError
from app.core.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    isolation_level="READ COMMITTED",
)
connections = ContextVar("connections", default=None)


class Record(Mapping):
    def __init__(self, row):
        self._values = tuple(row)
        self._mapping = dict(row._mapping)

    def __getitem__(self, key):
        return self._values[key] if isinstance(key, (int, slice)) else self._mapping[key]

    def __iter__(self):
        return iter(self._mapping)

    def __len__(self):
        return len(self._mapping)


class Cursor:
    def __init__(self, connection):
        self.connection = connection
        self.result = None
        self._lastrowid = None

    def execute(self, statement, parameters=()):
        # Repository values remain bound parameters, never interpolated into SQL.
        statement = statement.replace("%", "%%").replace("?", "%s")
        self.result = self.connection.native.exec_driver_sql(statement, tuple(parameters))
        self._lastrowid = self.result.lastrowid
        return self

    def executemany(self, statement, parameters):
        self.result = self.connection.native.exec_driver_sql(
            statement.replace("%", "%%").replace("?", "%s"), [tuple(p) for p in parameters]
        )
        return self

    def fetchone(self):
        row = self.result.fetchone()
        return Record(row) if row is not None else None

    def fetchall(self):
        return [Record(row) for row in self.result.fetchall()]

    @property
    def lastrowid(self):
        return self._lastrowid

    @property
    def rowcount(self):
        return self.result.rowcount


class Connection:
    def __init__(self):
        self.native = engine.connect()

    def cursor(self):
        return Cursor(self)

    def execute(self, statement, parameters=()):
        return self.cursor().execute(statement, parameters)

    def commit(self):
        self.native.commit()

    def rollback(self):
        self.native.rollback()

    def close(self):
        self.native.close()


def get_connection(*, write=False):
    connection = Connection()
    active = connections.get()
    if active is not None:
        active.append(connection)
    if write:
        # Serialize application writes before availability reads, preserving the
        # original checkout/return guarantees across app connections.
        try:
            connection.native.exec_driver_sql(
                "SELECT id FROM app_settings WHERE id = 1 FOR UPDATE"
            ).scalar_one()
        except Exception:
            connection.close()
            raise
    return connection


class ConnectionCleanupMiddleware:
    """Close and roll back abandoned connections even when an endpoint raises."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        active = []
        token = connections.set(active)
        try:
            await self.app(scope, receive, send)
        finally:
            for connection in reversed(active):
                connection.close()
            connections.reset(token)
