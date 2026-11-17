from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.services import history as handlers

router = APIRouter()

router.add_api_route("/history/export-selected", handlers.export_selected_history, methods=["POST"])
router.add_api_route("/history", handlers.history_redirect, methods=["GET"])
router.add_api_route(
    "/history/missions", handlers.mission_history_page, methods=["GET"], response_class=HTMLResponse
)
router.add_api_route(
    "/history/individual",
    handlers.individual_history_page,
    methods=["GET"],
    response_class=HTMLResponse,
)
