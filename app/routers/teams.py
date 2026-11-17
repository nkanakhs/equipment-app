from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.services import teams as handlers

router = APIRouter()

router.add_api_route("/teams", handlers.teams_page, methods=["GET"], response_class=HTMLResponse)
router.add_api_route("/teams/new", handlers.create_team, methods=["POST"])
router.add_api_route("/teams/{team_id}/edit", handlers.edit_team, methods=["POST"])
router.add_api_route("/teams/{team_id}/delete", handlers.delete_team, methods=["POST"])
router.add_api_route("/teams/vehicles/new", handlers.create_mission_vehicle, methods=["POST"])
router.add_api_route(
    "/teams/vehicles/{vehicle_id}/delete", handlers.delete_mission_vehicle, methods=["POST"]
)
router.add_api_route(
    "/teams/destinations/new", handlers.create_mission_destination, methods=["POST"]
)
router.add_api_route(
    "/teams/destinations/{destination_id}/edit", handlers.edit_mission_destination, methods=["POST"]
)
router.add_api_route(
    "/teams/destinations/{destination_id}/delete",
    handlers.delete_mission_destination,
    methods=["POST"],
)
