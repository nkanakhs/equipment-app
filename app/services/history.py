from fastapi import Request, Form, HTTPException
from fastapi.responses import RedirectResponse, Response
from datetime import datetime
import csv
import io
from app.db.session import get_connection
from app.core.templating import templates
from app.services.settings import get_settings
from app.repositories import history as queries


def export_selected_history(selected_items: list[str] = Form(...)):
    connection = get_connection(write=True)
    cursor = connection.cursor()
    rows = []
    for selected in selected_items:
        if ":" not in selected:
            continue
        (item_type, raw_id) = selected.split(":", 1)
        try:
            item_id = int(raw_id)
        except ValueError:
            continue
        if item_type == "mission":
            mission = queries.export_selected_history_1(cursor, (item_id,)).fetchone()
            if mission is None:
                continue
            mission_items = queries.export_selected_history_2(cursor, (item_id,)).fetchall()
            if not mission_items:
                rows.append(
                    {
                        "type": "Εκτός έδρας χρέωση",
                        "reference": mission["mission_code"] or f"Αποστολή #{mission['id']}",
                        "equipment": "",
                        "serial_number": "",
                        "dei_registry_number": "",
                        "tem_internal_code": "",
                        "team": mission["team_name"] or "",
                        "destination": mission["destination"] or "",
                        "vehicle": mission["vehicle"] or "",
                        "license_plate": mission["license_plate"] or "",
                        "checkout_date": mission["departure_date"] or "",
                        "return_date": "",
                        "status": mission["status"] or "",
                    }
                )
            else:
                for mission_item in mission_items:
                    equipment_text = mission_item["description"] or ""
                    if mission_item["manufacturer"]:
                        equipment_text += f" · {mission_item['manufacturer']}"
                    if mission_item["model"]:
                        equipment_text += f" {mission_item['model']}"
                    rows.append(
                        {
                            "type": "Εκτός έδρας χρέωση",
                            "reference": mission["mission_code"] or f"Αποστολή #{mission['id']}",
                            "equipment": equipment_text,
                            "serial_number": mission_item["serial_number"] or "",
                            "dei_registry_number": mission_item["dei_registry_number"] or "",
                            "tem_internal_code": mission_item["tem_internal_code"] or "",
                            "team": mission["team_name"] or "",
                            "destination": mission["destination"] or "",
                            "vehicle": mission["vehicle"] or "",
                            "license_plate": mission["license_plate"] or "",
                            "checkout_date": mission["departure_date"] or "",
                            "return_date": mission_item["mission_item_returned_at"] or "",
                            "status": mission_item["mission_item_status"]
                            or mission["status"]
                            or "",
                        }
                    )
        elif item_type == "loan":
            loan = queries.export_selected_history_3(cursor, (item_id,)).fetchone()
            if loan is None:
                continue
            equipment_text = loan["description"] or ""
            if loan["manufacturer"]:
                equipment_text += f" · {loan['manufacturer']}"
            if loan["model"]:
                equipment_text += f" {loan['model']}"
            rows.append(
                {
                    "type": "Μεμονωμένη χρέωση",
                    "reference": f"Χρέωση #{loan['id']}",
                    "equipment": equipment_text,
                    "serial_number": loan["serial_number"] or "",
                    "dei_registry_number": loan["dei_registry_number"] or "",
                    "tem_internal_code": loan["tem_internal_code"] or "",
                    "team": loan["borrower_name"] or "",
                    "destination": "",
                    "vehicle": "",
                    "license_plate": "",
                    "checkout_date": loan["checkout_date"] or "",
                    "return_date": loan["return_date"] or "",
                    "status": "Σε Χρήση" if loan["active"] == 1 else "Επεστράφη",
                }
            )
    connection.close()
    if not rows:
        raise HTTPException(status_code=400, detail="Δεν επιλέχθηκε έγκυρη χρέωση για εξαγωγή.")
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow(
        [
            "Τύπος",
            "Αναφορά",
            "Εξοπλισμός",
            "Serial Number",
            "Αρ. Μητρώου ΔΕΗ",
            "Κωδικός ΤΕΜ",
            "Ομάδα Μετρήσεων",
            "Σταθμός / Προορισμός",
            "Όχημα",
            "Πινακίδα",
            "Ημερομηνία Χρέωσης / Αναχώρησης",
            "Ημερομηνία Επιστροφής / Ολοκλήρωσης",
            "Κατάσταση",
        ]
    )
    for row in rows:
        writer.writerow(
            [
                row["type"],
                row["reference"],
                row["equipment"],
                row["serial_number"],
                row["dei_registry_number"],
                row["tem_internal_code"],
                row["team"],
                row["destination"],
                row["vehicle"],
                row["license_plate"],
                row["checkout_date"],
                row["return_date"],
                row["status"],
            ]
        )
    csv_bytes = ("\ufeff" + output.getvalue()).encode("utf-8")
    filename = "selected_history_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".csv"
    return Response(
        content=csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def history_redirect():
    return RedirectResponse(url="/history/missions", status_code=303)


def mission_history_page(
    request: Request, destination: str = "", team: str = "", year: str = "", page: int = 1
):
    connection = get_connection()
    cursor = connection.cursor()
    page = max(1, page)
    per_page = 25
    filters = []
    parameters = []
    if destination:
        filters.append(queries.MISSION_HISTORY_PAGE_SQL_1)
        parameters.append(destination)
    if team:
        filters.append(queries.MISSION_HISTORY_PAGE_SQL_2)
        parameters.append(team)
    if year:
        filters.append(queries.MISSION_HISTORY_PAGE_SQL_3)
        parameters.append(year)
    where_clause = ""
    if filters:
        where_clause = queries.MISSION_HISTORY_PAGE_SQL_4 + queries.MISSION_HISTORY_PAGE_SQL_5.join(
            filters
        )
    total_count = queries.mission_history_page_1(cursor, parameters, where_clause).fetchone()[0]
    total_pages = max(1, (total_count + per_page - 1) // per_page)
    page = min(page, total_pages)
    offset = (page - 1) * per_page
    mission_history = queries.mission_history_page_2(
        cursor, parameters + [per_page, offset], where_clause
    ).fetchall()
    destinations = queries.mission_history_page_3(cursor, ()).fetchall()
    teams = queries.mission_history_page_4(cursor, ()).fetchall()
    years = queries.mission_history_page_5(cursor, ()).fetchall()
    connection.close()
    return templates.TemplateResponse(
        request=request,
        name="history_missions.html",
        context={
            "mission_history": mission_history,
            "destinations": destinations,
            "teams": teams,
            "years": years,
            "selected_destination": destination,
            "selected_team": team,
            "selected_year": year,
            "page": page,
            "per_page": per_page,
            "total_count": total_count,
            "total_pages": total_pages,
            "settings": get_settings(),
        },
    )


def individual_history_page(request: Request, year: str = "", page: int = 1):
    connection = get_connection()
    cursor = connection.cursor()
    page = max(1, page)
    per_page = 25
    parameters = []
    where_clause = ""
    if year:
        where_clause = queries.INDIVIDUAL_HISTORY_PAGE_SQL_6
        parameters.append(year)
    total_count = queries.individual_history_page_1(cursor, parameters, where_clause).fetchone()[0]
    total_pages = max(1, (total_count + per_page - 1) // per_page)
    page = min(page, total_pages)
    offset = (page - 1) * per_page
    history = queries.individual_history_page_2(
        cursor, parameters + [per_page, offset], where_clause
    ).fetchall()
    years = queries.individual_history_page_3(cursor, ()).fetchall()
    connection.close()
    return templates.TemplateResponse(
        request=request,
        name="history_individual.html",
        context={
            "history": history,
            "years": years,
            "selected_year": year,
            "page": page,
            "per_page": per_page,
            "total_count": total_count,
            "total_pages": total_pages,
            "settings": get_settings(),
        },
    )
