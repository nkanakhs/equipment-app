from fastapi import Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from datetime import datetime
from app.core.config import settings
from app.db.session import get_connection, IntegrityError
from app.core.templating import templates
from app.core.presentation import toast_redirect_url
from app.core.security import hash_password, verify_password
from app.services.sessions import (
    count_active_admins,
    create_user_session,
    delete_user_session,
    get_user_from_request,
)
from app.services.settings import get_settings
from app.core.security import SESSION_COOKIE_NAME
from app.core.security import SESSION_DAYS
from app.repositories import auth as queries


def login_page(request: Request, next: str = "/"):
    current = get_user_from_request(request)
    if current is not None:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "settings": get_settings(),
            "error": "",
            "next_path": next if next.startswith("/") else "/",
        },
    )


def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    next_path: str = Form("/"),
):
    connection = get_connection(write=True)
    try:
        user = queries.login_1(connection, (username.strip(),)).fetchone()
        valid = (
            user is not None
            and user["active"] == 1
            and verify_password(password, user["password_hash"])
        )
        if not valid:
            return templates.TemplateResponse(
                request=request,
                name="login.html",
                context={
                    "settings": get_settings(),
                    "error": "Λανθασμένο username ή password.",
                    "next_path": next_path if next_path.startswith("/") else "/",
                },
                status_code=401,
            )
        queries.login_2(connection, (datetime.now().isoformat(timespec="seconds"), user["id"]))
        connection.commit()
    finally:
        connection.close()
    token = create_user_session(user["id"])
    response = RedirectResponse(next_path if next_path.startswith("/") else "/", status_code=303)
    response.set_cookie(
        SESSION_COOKIE_NAME,
        token,
        httponly=True,
        samesite="lax",
        max_age=SESSION_DAYS * 24 * 60 * 60,
        secure=settings.cookie_secure,
    )
    return response


def logout(request: Request):
    delete_user_session(request)
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie(SESSION_COOKIE_NAME)
    return response


def account_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="account.html",
        context={"settings": get_settings(), "current_user": request.state.current_user},
    )


def account_change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    new_password_confirm: str = Form(...),
):
    user = request.state.current_user
    if not verify_password(current_password, user["password_hash"]):
        return RedirectResponse(
            toast_redirect_url("/account", "Ο τρέχων κωδικός δεν είναι σωστός.", "error"),
            status_code=303,
        )
    if len(new_password) < 8:
        return RedirectResponse(
            toast_redirect_url(
                "/account", "Ο νέος κωδικός πρέπει να έχει τουλάχιστον 8 χαρακτήρες.", "error"
            ),
            status_code=303,
        )
    if new_password != new_password_confirm:
        return RedirectResponse(
            toast_redirect_url("/account", "Οι νέοι κωδικοί δεν ταιριάζουν.", "error"),
            status_code=303,
        )
    connection = get_connection(write=True)
    try:
        queries.account_change_password_1(connection, (hash_password(new_password), user["id"]))
        queries.account_change_password_2(connection, (user["id"],))
        connection.commit()
    finally:
        connection.close()
    response = RedirectResponse("/login?changed=1", status_code=303)
    response.delete_cookie(SESSION_COOKIE_NAME)
    return response


def admin_create_user(
    request: Request,
    full_name: str = Form(...),
    username: str = Form(...),
    role: str = Form("USER"),
    password: str = Form(...),
):
    current = request.state.current_user
    if current["role"] != "ADMIN":
        raise HTTPException(status_code=403)
    full_name = full_name.strip()
    username = username.strip()
    role = role if role in {"ADMIN", "USER"} else "USER"
    if len(password) < 8:
        return RedirectResponse(
            toast_redirect_url(
                "/settings#users", "Ο κωδικός πρέπει να έχει τουλάχιστον 8 χαρακτήρες.", "error"
            ),
            status_code=303,
        )
    connection = get_connection(write=True)
    try:
        try:
            queries.admin_create_user_1(
                connection,
                (
                    username,
                    hash_password(password),
                    full_name,
                    role,
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )
            connection.commit()
        except IntegrityError:
            return RedirectResponse(
                toast_redirect_url("/settings#users", "Το username χρησιμοποιείται ήδη.", "error"),
                status_code=303,
            )
    finally:
        connection.close()
    return RedirectResponse(
        toast_redirect_url("/settings#users", "Ο χρήστης δημιουργήθηκε."), status_code=303
    )


def admin_update_user(
    request: Request,
    user_id: int,
    full_name: str = Form(...),
    username: str = Form(...),
    role: str = Form("USER"),
    active: int = Form(0),
):
    current = request.state.current_user
    if current["role"] != "ADMIN":
        raise HTTPException(status_code=403)
    full_name = full_name.strip()
    username = username.strip()
    role = role if role in {"ADMIN", "USER"} else "USER"
    active_value = 1 if active == 1 else 0
    if not full_name or not username:
        return RedirectResponse(
            toast_redirect_url(
                "/settings#users", "Ονοματεπώνυμο και username είναι υποχρεωτικά.", "error"
            ),
            status_code=303,
        )
    connection = get_connection(write=True)
    try:
        cursor = connection.cursor()
        target = queries.admin_update_user_1(cursor, (user_id,)).fetchone()
        if target is None:
            raise HTTPException(status_code=404)
        duplicate_username = queries.admin_update_user_2(cursor, (user_id, username)).fetchone()
        if duplicate_username is not None:
            return RedirectResponse(
                toast_redirect_url(
                    "/settings#users", "Το username χρησιμοποιείται ήδη από άλλον χρήστη.", "error"
                ),
                status_code=303,
            )
        if user_id == current["id"] and active_value == 0:
            return RedirectResponse(
                toast_redirect_url(
                    "/settings#users",
                    "Δεν μπορείτε να απενεργοποιήσετε τον λογαριασμό σας.",
                    "error",
                ),
                status_code=303,
            )
        removing_admin = (
            target["role"] == "ADMIN"
            and target["active"] == 1
            and (role != "ADMIN" or active_value == 0)
        )
        if removing_admin and count_active_admins(cursor) <= 1:
            return RedirectResponse(
                toast_redirect_url(
                    "/settings#users",
                    "Πρέπει να παραμείνει τουλάχιστον ένας ενεργός Admin.",
                    "error",
                ),
                status_code=303,
            )
        queries.admin_update_user_3(cursor, (full_name, username, role, active_value, user_id))
        if active_value == 0:
            queries.admin_update_user_4(cursor, (user_id,))
        connection.commit()
    finally:
        connection.close()
    return RedirectResponse(
        toast_redirect_url("/settings#users", "Ο χρήστης ενημερώθηκε."), status_code=303
    )


def admin_reset_user_password(request: Request, user_id: int, new_password: str = Form(...)):
    current = request.state.current_user
    if current["role"] != "ADMIN":
        raise HTTPException(status_code=403)
    if len(new_password) < 8:
        return RedirectResponse(
            toast_redirect_url(
                "/settings#users",
                "Ο νέος κωδικός πρέπει να έχει τουλάχιστον 8 χαρακτήρες.",
                "error",
            ),
            status_code=303,
        )
    connection = get_connection(write=True)
    try:
        queries.admin_reset_user_password_1(connection, (hash_password(new_password), user_id))
        queries.admin_reset_user_password_2(connection, (user_id,))
        connection.commit()
    finally:
        connection.close()
    return RedirectResponse(
        toast_redirect_url("/settings#users", "Ο κωδικός επαναφέρθηκε."), status_code=303
    )
