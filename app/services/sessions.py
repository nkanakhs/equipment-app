from fastapi import Request
from datetime import datetime
import secrets
from app.db.session import get_connection
from app.core.security import _utc_now, session_token_hash
from app.core.security import SESSION_COOKIE_NAME
from app.core.security import SESSION_DAYS
from app.repositories import sessions as queries


def get_user_from_request(request: Request):
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        return None
    connection = get_connection()
    try:
        row = queries.get_user_from_request_1(
            connection, (session_token_hash(token), _utc_now().isoformat(timespec="seconds"))
        ).fetchone()
        return row
    finally:
        connection.close()


def create_user_session(user_id: int):
    raw_token = secrets.token_urlsafe(40)
    created = _utc_now()
    from datetime import timedelta

    expires = created + timedelta(days=SESSION_DAYS)
    connection = get_connection(write=True)
    try:
        queries.create_user_session_1(connection, (created.isoformat(timespec="seconds"),))
        queries.create_user_session_2(
            connection,
            (
                user_id,
                session_token_hash(raw_token),
                created.isoformat(timespec="seconds"),
                expires.isoformat(timespec="seconds"),
            ),
        )
        connection.commit()
    finally:
        connection.close()
    return raw_token


def delete_user_session(request: Request):
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        return
    connection = get_connection(write=True)
    try:
        queries.delete_user_session_1(connection, (session_token_hash(token),))
        connection.commit()
    finally:
        connection.close()


def audit_action(user, action: str, path: str):
    if user is None:
        return
    connection = get_connection(write=True)
    try:
        queries.audit_action_1(
            connection,
            (
                user["id"],
                user["username"],
                user["full_name"],
                user["role"],
                action,
                path,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        connection.commit()
    finally:
        connection.close()


def count_active_admins(cursor):
    row = queries.count_active_admins_1(cursor, ()).fetchone()
    return row["c"] if row else 0
