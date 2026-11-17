from fastapi import Request
from fastapi.responses import RedirectResponse, JSONResponse
import re
from app.core.templating import templates
from app.services.sessions import audit_action, get_user_from_request
from app.services.settings import get_settings
import logging
from starlette.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)


def is_public_path(path: str) -> bool:
    return path.startswith("/static/") or path in {"/login", "/favicon.ico", "/healthz"}


def user_can_access(user, request: Request) -> bool:
    if user is None:
        return False
    if user["role"] == "ADMIN":
        return True
    path = request.url.path
    method = request.method.upper()
    if method in {"GET", "HEAD"}:
        blocked_prefixes = ("/settings", "/checkout-return", "/exports/", "/equipment/new")
        if path.startswith(blocked_prefixes):
            return False
        if re.match("^/equipment/\\d+/(edit|delete)", path):
            return False
        return True
    if method == "POST":
        if path.startswith("/picking-lists/"):
            return True
        if path.startswith("/api/picking-lists/"):
            return True
        if path in {"/account/password", "/logout"}:
            return True
        return False
    return False


async def authentication_and_rbac(request: Request, call_next):
    path = request.url.path
    if is_public_path(path):
        request.state.current_user = None
        return await call_next(request)
    user = await run_in_threadpool(get_user_from_request, request)
    request.state.current_user = user
    if user is None:
        if path.startswith("/api/"):
            return JSONResponse({"detail": "Απαιτείται σύνδεση."}, status_code=401)
        return RedirectResponse("/login?next=" + str(request.url.path), status_code=303)
    if not user_can_access(user, request):
        if path.startswith("/api/"):
            return JSONResponse(
                {"detail": "Δεν έχετε δικαίωμα πρόσβασης σε αυτή τη λειτουργία."}, status_code=403
            )
        return templates.TemplateResponse(
            request=request,
            name="403.html",
            context={"settings": await run_in_threadpool(get_settings), "current_user": user},
            status_code=403,
        )
    response = await call_next(request)
    if (
        request.method.upper() in {"POST", "PUT", "PATCH", "DELETE"}
        and response.status_code < 400
        and (path not in {"/login", "/logout", "/account/password"})
    ):
        try:
            await run_in_threadpool(audit_action, user, request.method.upper(), path)
        except Exception:
            logger.exception("Could not record audit action")
    return response
