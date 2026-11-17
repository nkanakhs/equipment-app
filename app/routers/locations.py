from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.services import locations as handlers

router = APIRouter()

router.add_api_route(
    "/locations", handlers.locations_page, methods=["GET"], response_class=HTMLResponse
)
router.add_api_route("/locations/new", handlers.create_location, methods=["POST"])
router.add_api_route("/locations/{location_id}/edit", handlers.edit_location, methods=["POST"])
router.add_api_route("/locations/{location_id}/delete", handlers.delete_location, methods=["POST"])
