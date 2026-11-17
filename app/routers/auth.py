from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.services import auth as handlers

router = APIRouter()

router.add_api_route("/login", handlers.login_page, methods=["GET"], response_class=HTMLResponse)
router.add_api_route("/login", handlers.login, methods=["POST"])
router.add_api_route("/logout", handlers.logout, methods=["POST"])
router.add_api_route(
    "/account", handlers.account_page, methods=["GET"], response_class=HTMLResponse
)
router.add_api_route("/account/password", handlers.account_change_password, methods=["POST"])
router.add_api_route("/settings/users/new", handlers.admin_create_user, methods=["POST"])
router.add_api_route(
    "/settings/users/{user_id}/update", handlers.admin_update_user, methods=["POST"]
)
router.add_api_route(
    "/settings/users/{user_id}/reset-password", handlers.admin_reset_user_password, methods=["POST"]
)
