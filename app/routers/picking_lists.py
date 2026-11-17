from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.services import picking_lists as handlers

router = APIRouter()

router.add_api_route(
    "/picking-lists", handlers.picking_lists_page, methods=["GET"], response_class=HTMLResponse
)
router.add_api_route("/picking-lists/new", handlers.create_picking_list, methods=["POST"])
router.add_api_route(
    "/picking-lists/{list_id}/update", handlers.update_picking_list, methods=["POST"]
)
router.add_api_route(
    "/api/picking-lists/{list_id}/items/{equipment_id}",
    handlers.api_add_picking_item,
    methods=["POST"],
)
router.add_api_route(
    "/picking-lists/{list_id}/items/{item_id}/delete",
    handlers.delete_picking_item,
    methods=["POST"],
)
router.add_api_route(
    "/picking-lists/{list_id}/replace/{item_id}/{alternative_id}",
    handlers.replace_picking_item,
    methods=["POST"],
)
router.add_api_route(
    "/picking-lists/{list_id}/checkout", handlers.checkout_picking_list, methods=["POST"]
)
