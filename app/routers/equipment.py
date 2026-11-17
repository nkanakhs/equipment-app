from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.services import equipment as handlers

router = APIRouter()

router.add_api_route(
    "/equipment", handlers.equipment_list, methods=["GET"], response_class=HTMLResponse
)
router.add_api_route(
    "/api/equipment/{equipment_id}", handlers.equipment_panel_data, methods=["GET"]
)
router.add_api_route(
    "/equipment/{equipment_id}/documents", handlers.upload_equipment_document, methods=["POST"]
)
router.add_api_route(
    "/equipment/{equipment_id}/documents/{document_id}/delete",
    handlers.delete_equipment_document,
    methods=["POST"],
)
router.add_api_route(
    "/equipment/new", handlers.new_equipment_page, methods=["GET"], response_class=HTMLResponse
)
router.add_api_route("/equipment/new", handlers.create_equipment, methods=["POST"])
router.add_api_route(
    "/equipment/{equipment_id}/checkout", handlers.checkout_equipment, methods=["POST"]
)
router.add_api_route(
    "/equipment/{equipment_id}/delete", handlers.delete_equipment, methods=["POST"]
)
router.add_api_route(
    "/equipment/{equipment_id}/alternatives/add",
    handlers.add_equipment_alternative,
    methods=["POST"],
)
router.add_api_route(
    "/equipment/{equipment_id}/alternatives/{relation_id}/delete",
    handlers.delete_equipment_alternative,
    methods=["POST"],
)
router.add_api_route(
    "/equipment/{equipment_id}",
    handlers.equipment_detail,
    methods=["GET"],
    response_class=HTMLResponse,
)
router.add_api_route(
    "/equipment/{equipment_id}/edit",
    handlers.equipment_edit_page,
    methods=["GET"],
    response_class=HTMLResponse,
)
router.add_api_route("/equipment/{equipment_id}/edit", handlers.update_equipment, methods=["POST"])
