from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.services import dashboard as handlers

router = APIRouter()

router.add_api_route("/", handlers.home, methods=["GET"], response_class=HTMLResponse)
