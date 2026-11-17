from fastapi.templating import Jinja2Templates
from app.core.config import PROJECT_DIR
from app.core.presentation import format_date

templates = Jinja2Templates(directory=PROJECT_DIR / "app" / "templates")
templates.env.filters["date_gr"] = format_date
