from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.services import missions as handlers

router = APIRouter()

router.add_api_route(
    "/checkout-return", handlers.checkout_return_page, methods=["GET"], response_class=HTMLResponse
)
router.add_api_route("/loans/{loan_id}/return", handlers.return_equipment, methods=["POST"])
router.add_api_route(
    "/missions/{mission_id}",
    handlers.mission_detail_page,
    methods=["GET"],
    response_class=HTMLResponse,
)
router.add_api_route(
    "/missions/{mission_id}/delete", handlers.delete_field_mission, methods=["POST"]
)
router.add_api_route("/missions/new", handlers.create_field_mission, methods=["POST"])
router.add_api_route(
    "/missions/{mission_id}/picking-list/{list_id}/replace/{item_id}/{alternative_id}",
    handlers.mission_replace_picking_item,
    methods=["POST"],
)
router.add_api_route(
    "/missions/{mission_id}/picking-list/{list_id}/load",
    handlers.load_picking_list_into_mission,
    methods=["POST"],
)
router.add_api_route(
    "/missions/{mission_id}/items/add-bulk", handlers.add_mission_items_bulk, methods=["POST"]
)
router.add_api_route(
    "/missions/{mission_id}/items/add", handlers.add_equipment_to_mission, methods=["POST"]
)
router.add_api_route(
    "/missions/{mission_id}/items/{mission_item_id}/remove",
    handlers.remove_equipment_from_mission_draft,
    methods=["POST"],
)
router.add_api_route("/missions/{mission_id}/start", handlers.start_field_mission, methods=["POST"])
router.add_api_route(
    "/missions/{mission_id}/items/{mission_item_id}/return",
    handlers.return_mission_item,
    methods=["POST"],
)
router.add_api_route(
    "/missions/{mission_id}/return-all", handlers.return_all_mission_items, methods=["POST"]
)
router.add_api_route("/loans/{loan_id}/delete", handlers.delete_history_movement, methods=["POST"])
