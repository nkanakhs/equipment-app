from fastapi import Request, Form
from fastapi.responses import RedirectResponse, JSONResponse
from datetime import datetime
from app.db.session import get_connection, IntegrityError
from app.core.templating import templates
from app.core.presentation import toast_redirect_url
from app.services.settings import get_settings
from app.repositories import picking_lists as queries


def picking_lists_page(request: Request, list_id: int | None = None, q: str = ""):
    connection = get_connection()
    cursor = connection.cursor()
    lists = queries.picking_lists_page_1(cursor, ()).fetchall()
    selected = None
    items = []
    search_results = []
    if list_id is not None:
        selected = queries.picking_lists_page_2(cursor, (list_id,)).fetchone()
        if selected:
            items = queries.picking_lists_page_3(cursor, (list_id,)).fetchall()
            if q.strip():
                term = f"%{q.strip()}%"
                search_results = queries.picking_lists_page_4(
                    cursor, (list_id, term, term, term, term, term, term, term, term)
                ).fetchall()
    connection.close()
    return templates.TemplateResponse(
        request=request,
        name="picking_lists.html",
        context={
            "lists": lists,
            "selected": selected,
            "items": items,
            "q": q,
            "search_results": search_results,
            "settings": get_settings(),
        },
    )


def create_picking_list(
    title: str = Form(...),
    destination: str = Form(""),
    travel_date: str = Form(""),
    team_name: str = Form(""),
    notes: str = Form(""),
):
    now = datetime.now().isoformat(timespec="seconds")
    connection = get_connection(write=True)
    cursor = connection.cursor()
    queries.create_picking_list_1(
        cursor,
        (
            title.strip(),
            destination.strip(),
            travel_date.strip(),
            team_name.strip(),
            notes.strip(),
            now,
            now,
        ),
    )
    list_id = cursor.lastrowid
    code = f"PL-{datetime.now().year}-{list_id:04d}"
    queries.create_picking_list_2(cursor, (code, list_id))
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url(f"/picking-lists?list_id={list_id}", f"Δημιουργήθηκε η {code}."),
        status_code=303,
    )


def update_picking_list(
    list_id: int,
    title: str = Form(...),
    destination: str = Form(""),
    travel_date: str = Form(""),
    team_name: str = Form(""),
    notes: str = Form(""),
    status: str = Form("Draft"),
):
    allowed = {"Draft", "Έτοιμη", "Χρησιμοποιήθηκε"}
    if status not in allowed:
        status = "Draft"
    connection = get_connection(write=True)
    cursor = connection.cursor()
    queries.update_picking_list_1(
        cursor,
        (
            title.strip(),
            destination.strip(),
            travel_date.strip(),
            team_name.strip(),
            notes.strip(),
            status,
            datetime.now().isoformat(timespec="seconds"),
            list_id,
        ),
    )
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url(f"/picking-lists?list_id={list_id}", "Η Picking List ενημερώθηκε."),
        status_code=303,
    )


def api_add_picking_item(list_id: int, equipment_id: int):
    connection = get_connection(write=True)
    cursor = connection.cursor()
    plist = queries.api_add_picking_item_1(cursor, (list_id,)).fetchone()
    item = queries.api_add_picking_item_2(cursor, (equipment_id,)).fetchone()
    if not plist or not item:
        connection.close()
        return JSONResponse(
            {"ok": False, "message": "Η λίστα ή ο εξοπλισμός δεν βρέθηκε."}, status_code=404
        )
    alt = queries.api_add_picking_item_3(cursor, (equipment_id,)).fetchone()
    if item["status"] != "Διαθέσιμο":
        payload = {
            "ok": False,
            "unavailable": True,
            "message": f"Το {item['code']} — {item['description']} δεν είναι διαθέσιμο ({item['status']}).",
        }
        if alt:
            payload["alternative"] = {
                "id": alt["id"],
                "code": alt["code"],
                "description": alt["description"],
                "status": alt["status"],
            }
        connection.close()
        return JSONResponse(payload, status_code=409)
    try:
        queries.api_add_picking_item_4(
            cursor, (list_id, equipment_id, datetime.now().isoformat(timespec="seconds"))
        )
        queries.api_add_picking_item_5(
            cursor, (datetime.now().isoformat(timespec="seconds"), list_id)
        )
        connection.commit()
    except IntegrityError:
        connection.close()
        return JSONResponse(
            {"ok": False, "message": "Το υλικό υπάρχει ήδη στη λίστα."}, status_code=409
        )
    connection.close()
    return {"ok": True, "message": "Το υλικό προστέθηκε στη Picking List."}


def delete_picking_item(list_id: int, item_id: int):
    connection = get_connection(write=True)
    queries.delete_picking_item_1(connection, (item_id, list_id))
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url(f"/picking-lists?list_id={list_id}", "Το υλικό αφαιρέθηκε."),
        status_code=303,
    )


def replace_picking_item(list_id: int, item_id: int, alternative_id: int):
    connection = get_connection(write=True)
    cursor = connection.cursor()
    alt = queries.replace_picking_item_1(cursor, (alternative_id,)).fetchone()
    if not alt or alt["status"] != "Διαθέσιμο":
        connection.close()
        return RedirectResponse(
            url=toast_redirect_url(
                f"/checkout-return?tab=missions&picking_list_id={list_id}",
                "Η εναλλακτική δεν είναι πλέον διαθέσιμη.",
                "error",
            ),
            status_code=303,
        )
    try:
        queries.replace_picking_item_2(cursor, (alternative_id, item_id, list_id))
        connection.commit()
    except IntegrityError:
        connection.close()
        return RedirectResponse(
            url=toast_redirect_url(
                f"/checkout-return?tab=missions&picking_list_id={list_id}",
                "Η εναλλακτική υπάρχει ήδη στη λίστα.",
                "error",
            ),
            status_code=303,
        )
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url(
            f"/checkout-return?tab=missions&picking_list_id={list_id}",
            f"Χρησιμοποιήθηκε η εναλλακτική {alt['code']}.",
        ),
        status_code=303,
    )


def checkout_picking_list(
    list_id: int,
    borrower_name: str = Form(...),
    borrower_unit: str = Form(""),
    checkout_date: str = Form(...),
    expected_return_date: str = Form(""),
    checkout_notes: str = Form(""),
):
    connection = get_connection(write=True)
    cursor = connection.cursor()
    plist = queries.checkout_picking_list_1(cursor, (list_id,)).fetchone()
    items = queries.checkout_picking_list_2(cursor, (list_id,)).fetchall()
    if not plist or not items:
        connection.close()
        return RedirectResponse(
            url=toast_redirect_url(
                "/checkout-return?tab=missions", "Η Picking List δεν βρέθηκε ή είναι κενή.", "error"
            ),
            status_code=303,
        )
    unavailable = [x for x in items if x["status"] != "Διαθέσιμο"]
    if unavailable:
        connection.close()
        return RedirectResponse(
            url=toast_redirect_url(
                f"/checkout-return?tab=missions&picking_list_id={list_id}",
                f"Η χρέωση σταμάτησε: {len(unavailable)} υλικά δεν είναι πλέον διαθέσιμα.",
                "error",
            ),
            status_code=303,
        )
    now = datetime.now().isoformat(timespec="seconds")
    for item in items:
        queries.checkout_picking_list_3(
            cursor,
            (
                item["id"],
                borrower_name.strip(),
                borrower_unit.strip(),
                checkout_date.strip(),
                expected_return_date.strip(),
                checkout_notes.strip(),
                now,
            ),
        )
        queries.checkout_picking_list_4(cursor, (item["id"],))
    queries.checkout_picking_list_5(cursor, (now, list_id))
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url(
            "/checkout-return?tab=missions",
            f"Χρεώθηκαν {len(items)} υλικά από την {plist['list_code']}.",
        ),
        status_code=303,
    )
