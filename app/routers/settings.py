from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.services import settings as handlers

router = APIRouter()

router.add_api_route("/settings/headquarters/edit", handlers.edit_headquarters, methods=["POST"])
router.add_api_route(
    "/settings", handlers.settings_page, methods=["GET"], response_class=HTMLResponse
)
router.add_api_route("/settings", handlers.update_settings, methods=["POST"])
router.add_api_route("/settings/backup", handlers.download_backup, methods=["GET"])
router.add_api_route(
    "/exports/equipment-filtered", handlers.export_equipment_filtered, methods=["GET"]
)
