from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.services import categories as handlers

router = APIRouter()

router.add_api_route(
    "/categories", handlers.categories_page, methods=["GET"], response_class=HTMLResponse
)
router.add_api_route("/categories/new", handlers.create_category, methods=["POST"])
router.add_api_route("/categories/{category_id}/edit", handlers.edit_category, methods=["POST"])
router.add_api_route("/categories/{category_id}/delete", handlers.delete_category, methods=["POST"])
