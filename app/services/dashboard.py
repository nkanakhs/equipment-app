from fastapi import Request
from datetime import datetime
from app.db.session import get_connection
from app.core.templating import templates
from app.repositories import dashboard as queries


def home(request: Request):
    connection = get_connection()
    cursor = connection.cursor()
    today = datetime.now().date().isoformat()
    total = queries.home_1(cursor, ()).fetchone()[0]
    available = queries.home_2(cursor, ()).fetchone()[0]
    in_use = queries.home_3(cursor, ()).fetchone()[0]
    on_mission = queries.home_4(cursor, ()).fetchone()[0]
    in_use_total = in_use + on_mission
    maintenance = queries.home_5(cursor, ()).fetchone()[0]
    out_of_service = queries.home_6(cursor, ()).fetchone()[0]
    active_loans_count = queries.home_7(cursor, ()).fetchone()[0]
    recent_movements = queries.home_8(cursor, ()).fetchall()
    status_breakdown = queries.home_9(cursor, ()).fetchall()
    category_breakdown = queries.home_10(cursor, ()).fetchall()
    map_destinations = queries.home_11(cursor, ()).fetchall()
    active_map_missions = queries.home_12(cursor, ()).fetchall()
    settings = queries.home_13(cursor, ()).fetchone()
    connection.close()
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "today": today,
            "total": total,
            "available": available,
            "in_use": in_use,
            "on_mission": on_mission,
            "in_use_total": in_use_total,
            "maintenance": maintenance,
            "out_of_service": out_of_service,
            "active_loans_count": active_loans_count,
            "recent_movements": recent_movements,
            "status_breakdown": status_breakdown,
            "category_breakdown": category_breakdown,
            "map_destinations": map_destinations,
            "active_map_missions": active_map_missions,
            "headquarters": settings,
            "settings": settings,
        },
    )
