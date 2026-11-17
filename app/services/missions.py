from fastapi import Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from datetime import datetime
from app.db.session import get_connection, IntegrityError
from app.core.templating import templates
from app.core.presentation import toast_redirect_url
from app.services.settings import get_settings
from app.repositories import missions as queries


def checkout_return_page(
    request: Request,
    q: str = "",
    tab: str = "missions",
    mission_id: int | None = None,
    mission_q: str = "",
    picking_list_id: int | None = None,
):
    connection = get_connection()
    cursor = connection.cursor()
    if q:
        search_term = f"%{q}%"
        available_equipment = queries.checkout_return_page_1(
            cursor,
            (
                search_term,
                search_term,
                search_term,
                search_term,
                search_term,
                search_term,
                search_term,
                search_term,
                search_term,
                search_term,
                search_term,
            ),
        ).fetchall()
    else:
        available_equipment = []
    active_loans = queries.checkout_return_page_2(cursor, ()).fetchall()
    teams = queries.checkout_return_page_3(cursor, ()).fetchall()
    settings = queries.checkout_return_page_4(cursor, ()).fetchone()
    vehicles = queries.checkout_return_page_5(cursor, ()).fetchall()
    destinations = queries.checkout_return_page_6(cursor, ()).fetchall()
    missions = queries.checkout_return_page_7(cursor, ()).fetchall()
    selected_mission = None
    mission_items = []
    mission_available_equipment = []
    if mission_id is not None:
        selected_mission = queries.checkout_return_page_8(cursor, (mission_id,)).fetchone()
        if selected_mission is not None:
            mission_items = queries.checkout_return_page_9(cursor, (mission_id,)).fetchall()
            if selected_mission["status"] in ("Προετοιμασία", "Ενεργή") and mission_q:
                mission_search_term = f"%{mission_q}%"
                mission_available_equipment = queries.checkout_return_page_10(
                    cursor,
                    (
                        mission_id,
                        mission_search_term,
                        mission_search_term,
                        mission_search_term,
                        mission_search_term,
                        mission_search_term,
                        mission_search_term,
                        mission_search_term,
                        mission_search_term,
                        mission_search_term,
                        mission_search_term,
                        mission_search_term,
                    ),
                ).fetchall()
    picking_lists = queries.checkout_return_page_11(cursor, ()).fetchall()
    selected_picking_list = None
    picking_checkout_items = []
    if picking_list_id is not None:
        selected_picking_list = queries.checkout_return_page_12(
            cursor, (picking_list_id,)
        ).fetchone()
        if selected_picking_list is not None:
            picking_checkout_items = queries.checkout_return_page_13(
                cursor, (picking_list_id,)
            ).fetchall()
    connection.close()
    return templates.TemplateResponse(
        request=request,
        name="checkout_return.html",
        context={
            "available_equipment": available_equipment,
            "active_loans": active_loans,
            "teams": teams,
            "vehicles": vehicles,
            "destinations": destinations,
            "settings": settings,
            "q": q,
            "tab": tab,
            "missions": missions,
            "selected_mission": selected_mission,
            "mission_items": mission_items,
            "mission_q": mission_q,
            "mission_available_equipment": mission_available_equipment,
            "picking_lists": picking_lists,
            "selected_picking_list": selected_picking_list,
            "picking_checkout_items": picking_checkout_items,
            "picking_list_id": picking_list_id,
        },
    )


def return_equipment(loan_id: int, return_date: str = Form(...), return_notes: str = Form("")):
    connection = get_connection(write=True)
    cursor = connection.cursor()
    loan = queries.return_equipment_1(cursor, (loan_id,)).fetchone()
    if loan is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Η ενεργή χρέωση δεν βρέθηκε.")
    queries.return_equipment_2(cursor, (return_date.strip(), return_notes.strip(), loan_id))
    queries.return_equipment_3(cursor, (loan["equipment_id"],))
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url("/checkout-return", "Η επιστροφή ολοκληρώθηκε επιτυχώς."),
        status_code=303,
    )


def mission_detail_page(
    request: Request, mission_id: int, mission_q: str = "", picking_list_id: int | None = None
):
    connection = get_connection()
    cursor = connection.cursor()
    selected_mission = queries.mission_detail_page_1(cursor, (mission_id,)).fetchone()
    if selected_mission is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Η αποστολή δεν βρέθηκε.")
    mission_items = queries.mission_detail_page_2(cursor, (mission_id,)).fetchall()
    mission_available_equipment = []
    if selected_mission["status"] in ("Προετοιμασία", "Ενεργή") and mission_q:
        mission_search_term = f"%{mission_q}%"
        mission_available_equipment = queries.mission_detail_page_3(
            cursor,
            (
                mission_id,
                mission_search_term,
                mission_search_term,
                mission_search_term,
                mission_search_term,
                mission_search_term,
                mission_search_term,
                mission_search_term,
                mission_search_term,
                mission_search_term,
                mission_search_term,
                mission_search_term,
            ),
        ).fetchall()
    picking_lists = queries.mission_detail_page_4(cursor, ()).fetchall()
    selected_picking_list = None
    mission_picking_items = []
    if picking_list_id is not None:
        selected_picking_list = queries.mission_detail_page_5(cursor, (picking_list_id,)).fetchone()
        if selected_picking_list is not None:
            mission_picking_items = queries.mission_detail_page_6(
                cursor, (picking_list_id,)
            ).fetchall()
    connection.close()
    return templates.TemplateResponse(
        request=request,
        name="mission_detail.html",
        context={
            "selected_mission": selected_mission,
            "mission_items": mission_items,
            "mission_q": mission_q,
            "mission_available_equipment": mission_available_equipment,
            "picking_lists": picking_lists,
            "selected_picking_list": selected_picking_list,
            "mission_picking_items": mission_picking_items,
            "picking_list_id": picking_list_id,
            "settings": get_settings(),
        },
    )


def delete_field_mission(mission_id: int):
    connection = get_connection(write=True)
    cursor = connection.cursor()
    mission = queries.delete_field_mission_1(cursor, (mission_id,)).fetchone()
    if mission is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Η αποστολή δεν βρέθηκε.")
    mission_items = queries.delete_field_mission_2(cursor, (mission_id,)).fetchall()
    for item in mission_items:
        if item["status"] == "Σε Αποστολή":
            queries.delete_field_mission_3(cursor, (item["equipment_id"],))
    queries.delete_field_mission_4(cursor, (mission_id,))
    queries.delete_field_mission_5(cursor, (mission_id,))
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url("/history/missions", "Η αποστολή διαγράφηκε επιτυχώς."),
        status_code=303,
    )


def create_field_mission(
    destination: str = Form(...),
    team_name: str = Form(...),
    departure_date: str = Form(...),
    vehicle: str = Form(""),
    license_plate: str = Form(""),
    notes: str = Form(""),
):
    destination = destination.strip()
    team_name = team_name.strip()
    departure_date = departure_date.strip()
    if not destination or not team_name or (not departure_date):
        raise HTTPException(
            status_code=400,
            detail="Σταθμός / Προορισμός, Ομάδα και Ημερομηνία Αναχώρησης είναι υποχρεωτικά.",
        )
    connection = get_connection(write=True)
    cursor = connection.cursor()
    queries.create_field_mission_1(
        cursor,
        (
            destination,
            team_name,
            departure_date,
            "",
            vehicle.strip(),
            license_plate.strip().upper(),
            notes.strip(),
            datetime.now().isoformat(timespec="seconds"),
        ),
    )
    mission_id = cursor.lastrowid
    mission_code = "ΑΠ-" + str(datetime.now().year) + "-" + str(mission_id).zfill(3)
    queries.create_field_mission_2(cursor, (mission_code, mission_id))
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url(
            f"/missions/{mission_id}", f"Η αποστολή {mission_code} δημιουργήθηκε."
        ),
        status_code=303,
    )


def mission_replace_picking_item(mission_id: int, list_id: int, item_id: int, alternative_id: int):
    connection = get_connection(write=True)
    cursor = connection.cursor()
    mission = queries.mission_replace_picking_item_1(cursor, (mission_id,)).fetchone()
    if mission is None or mission["status"] not in ("Προετοιμασία", "Ενεργή"):
        connection.close()
        return RedirectResponse(
            url=toast_redirect_url(
                f"/missions/{mission_id}",
                "Η αποστολή δεν είναι διαθέσιμη για προσθήκη εξοπλισμού.",
                "error",
            ),
            status_code=303,
        )
    alt = queries.mission_replace_picking_item_2(cursor, (alternative_id,)).fetchone()
    if alt is None or alt["status"] != "Διαθέσιμο":
        connection.close()
        return RedirectResponse(
            url=toast_redirect_url(
                f"/missions/{mission_id}?picking_list_id={list_id}",
                "Η εναλλακτική δεν είναι πλέον διαθέσιμη.",
                "error",
            ),
            status_code=303,
        )
    try:
        queries.mission_replace_picking_item_3(cursor, (alternative_id, item_id, list_id))
        connection.commit()
    except IntegrityError:
        connection.close()
        return RedirectResponse(
            url=toast_redirect_url(
                f"/missions/{mission_id}?picking_list_id={list_id}",
                "Η εναλλακτική υπάρχει ήδη στη Picking List.",
                "error",
            ),
            status_code=303,
        )
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url(
            f"/missions/{mission_id}?picking_list_id={list_id}",
            f"Χρησιμοποιήθηκε η εναλλακτική {alt['code']}.",
        ),
        status_code=303,
    )


def load_picking_list_into_mission(mission_id: int, list_id: int):
    connection = get_connection(write=True)
    cursor = connection.cursor()
    mission = queries.load_picking_list_into_mission_1(cursor, (mission_id,)).fetchone()
    if mission is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Η αποστολή δεν βρέθηκε.")
    if mission["status"] not in ("Προετοιμασία", "Ενεργή"):
        connection.close()
        return RedirectResponse(
            url=toast_redirect_url(
                f"/missions/{mission_id}",
                "Δεν μπορεί να φορτωθεί Picking List σε ολοκληρωμένη αποστολή.",
                "error",
            ),
            status_code=303,
        )
    plist = queries.load_picking_list_into_mission_2(cursor, (list_id,)).fetchone()
    items = queries.load_picking_list_into_mission_3(cursor, (list_id,)).fetchall()
    if plist is None or not items:
        connection.close()
        return RedirectResponse(
            url=toast_redirect_url(
                f"/missions/{mission_id}", "Η Picking List δεν βρέθηκε ή είναι κενή.", "error"
            ),
            status_code=303,
        )
    unavailable = [e for e in items if e["status"] != "Διαθέσιμο"]
    if unavailable:
        connection.close()
        return RedirectResponse(
            url=toast_redirect_url(
                f"/missions/{mission_id}?picking_list_id={list_id}",
                f"Η φόρτωση σταμάτησε: {len(unavailable)} υλικά δεν είναι διαθέσιμα.",
                "error",
            ),
            status_code=303,
        )
    added_count = 0
    item_status = "Σε Αποστολή" if mission["status"] == "Ενεργή" else "Προετοιμασία"
    now = datetime.now().isoformat(timespec="seconds")
    for equipment in items:
        already_added = queries.load_picking_list_into_mission_4(
            cursor, (mission_id, equipment["id"])
        ).fetchone()
        if already_added is not None:
            continue
        queries.load_picking_list_into_mission_5(
            cursor, (mission_id, equipment["id"], item_status, now)
        )
        if mission["status"] == "Ενεργή":
            queries.load_picking_list_into_mission_6(cursor, (equipment["id"],))
        added_count += 1
    queries.load_picking_list_into_mission_7(cursor, (now, list_id))
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url(
            f"/missions/{mission_id}",
            f"Η Picking List {plist['list_code']} φορτώθηκε στην αποστολή ({added_count} νέα υλικά).",
        ),
        status_code=303,
    )


def add_mission_items_bulk(mission_id: int, equipment_ids: list[int] = Form(...)):
    connection = get_connection(write=True)
    cursor = connection.cursor()
    mission = queries.add_mission_items_bulk_1(cursor, (mission_id,)).fetchone()
    if mission is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Η αποστολή δεν βρέθηκε.")
    if mission["status"] not in ("Προετοιμασία", "Ενεργή"):
        connection.close()
        raise HTTPException(
            status_code=400, detail="Δεν μπορεί να προστεθεί εξοπλισμός σε ολοκληρωμένη αποστολή."
        )
    unique_ids = list(dict.fromkeys(equipment_ids))
    added_count = 0
    for equipment_id in unique_ids:
        equipment = queries.add_mission_items_bulk_2(cursor, (equipment_id,)).fetchone()
        if equipment is None:
            continue
        if equipment["status"] != "Διαθέσιμο":
            continue
        already_added = queries.add_mission_items_bulk_3(
            cursor, (mission_id, equipment_id)
        ).fetchone()
        if already_added is not None:
            continue
        item_status = "Σε Αποστολή" if mission["status"] == "Ενεργή" else "Προετοιμασία"
        queries.add_mission_items_bulk_4(
            cursor,
            (mission_id, equipment_id, item_status, datetime.now().isoformat(timespec="seconds")),
        )
        if mission["status"] == "Ενεργή":
            queries.add_mission_items_bulk_5(cursor, (equipment_id,))
        added_count += 1
    connection.commit()
    connection.close()
    message = (
        f"Προστέθηκαν {added_count} αντικείμενα στην αποστολή."
        if added_count != 1
        else "Προστέθηκε 1 αντικείμενο στην αποστολή."
    )
    return RedirectResponse(
        url=toast_redirect_url(f"/missions/{mission_id}", message), status_code=303
    )


def add_equipment_to_mission(mission_id: int, equipment_id: int = Form(...)):
    connection = get_connection(write=True)
    cursor = connection.cursor()
    mission = queries.add_equipment_to_mission_1(cursor, (mission_id,)).fetchone()
    if mission is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Η αποστολή δεν βρέθηκε.")
    if mission["status"] not in ("Προετοιμασία", "Ενεργή"):
        connection.close()
        raise HTTPException(
            status_code=400, detail="Δεν μπορεί να προστεθεί εξοπλισμός σε ολοκληρωμένη αποστολή."
        )
    equipment = queries.add_equipment_to_mission_2(cursor, (equipment_id,)).fetchone()
    if equipment is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Ο εξοπλισμός δεν βρέθηκε.")
    if equipment["status"] != "Διαθέσιμο":
        connection.close()
        raise HTTPException(status_code=400, detail="Ο εξοπλισμός δεν είναι διαθέσιμος.")
    item_status = "Σε Αποστολή" if mission["status"] == "Ενεργή" else "Προετοιμασία"
    try:
        queries.add_equipment_to_mission_3(
            cursor,
            (mission_id, equipment_id, item_status, datetime.now().isoformat(timespec="seconds")),
        )
        if mission["status"] == "Ενεργή":
            queries.add_equipment_to_mission_4(cursor, (equipment_id,))
        connection.commit()
    except IntegrityError:
        connection.close()
        raise HTTPException(
            status_code=400, detail="Ο εξοπλισμός βρίσκεται ήδη στη λίστα της αποστολής."
        )
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url(f"/missions/{mission_id}", "Ο εξοπλισμός προστέθηκε στη λίστα."),
        status_code=303,
    )


def remove_equipment_from_mission_draft(mission_id: int, mission_item_id: int):
    connection = get_connection(write=True)
    cursor = connection.cursor()
    mission = queries.remove_equipment_from_mission_draft_1(cursor, (mission_id,)).fetchone()
    if mission is None or mission["status"] != "Προετοιμασία":
        connection.close()
        raise HTTPException(
            status_code=400, detail="Η αφαίρεση είναι διαθέσιμη μόνο στην προετοιμασία."
        )
    queries.remove_equipment_from_mission_draft_2(cursor, (mission_item_id, mission_id))
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url(f"/missions/{mission_id}", "Ο εξοπλισμός αφαιρέθηκε από τη λίστα."),
        status_code=303,
    )


def start_field_mission(mission_id: int):
    connection = get_connection(write=True)
    cursor = connection.cursor()
    mission = queries.start_field_mission_1(cursor, (mission_id,)).fetchone()
    if mission is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Η αποστολή δεν βρέθηκε.")
    if mission["status"] != "Προετοιμασία":
        connection.close()
        raise HTTPException(status_code=400, detail="Η αποστολή έχει ήδη ξεκινήσει.")
    items = queries.start_field_mission_2(cursor, (mission_id,)).fetchall()
    if not items:
        connection.close()
        raise HTTPException(status_code=400, detail="Προσθέστε τουλάχιστον ένα κομμάτι εξοπλισμού.")
    unavailable = [item for item in items if item["equipment_status"] != "Διαθέσιμο"]
    if unavailable:
        connection.close()
        raise HTTPException(
            status_code=400, detail="Κάποιος εξοπλισμός της λίστας δεν είναι πλέον διαθέσιμος."
        )
    equipment_ids = [item["equipment_id"] for item in items]
    placeholders = ",".join(("?" for _ in equipment_ids))
    queries.start_field_mission_3(cursor, equipment_ids, placeholders)
    queries.start_field_mission_4(cursor, (mission_id,))
    queries.start_field_mission_5(cursor, (mission_id,))
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url(f"/missions/{mission_id}", "Η εκτός έδρας αποστολή ξεκίνησε."),
        status_code=303,
    )


def return_mission_item(
    mission_id: int,
    mission_item_id: int,
    return_date: str = Form(...),
    return_notes: str = Form(""),
):
    connection = get_connection(write=True)
    cursor = connection.cursor()
    item = queries.return_mission_item_1(cursor, (mission_item_id, mission_id)).fetchone()
    if item is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Το ενεργό υλικό της αποστολής δεν βρέθηκε.")
    queries.return_mission_item_2(
        cursor, (return_date.strip(), return_notes.strip(), mission_item_id)
    )
    queries.return_mission_item_3(cursor, (item["equipment_id"],))
    remaining = queries.return_mission_item_4(cursor, (mission_id, mission_item_id)).fetchone()[0]
    if remaining == 0:
        queries.return_mission_item_5(
            cursor, (datetime.now().isoformat(timespec="seconds"), mission_id)
        )
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url(f"/missions/{mission_id}", "Το υλικό επέστρεψε στα ράφια."),
        status_code=303,
    )


def return_all_mission_items(
    mission_id: int, return_date: str = Form(...), return_notes: str = Form("")
):
    connection = get_connection(write=True)
    cursor = connection.cursor()
    active_items = queries.return_all_mission_items_1(cursor, (mission_id,)).fetchall()
    if not active_items:
        connection.close()
        raise HTTPException(
            status_code=400, detail="Δεν υπάρχουν υλικά προς επιστροφή σε αυτή την αποστολή."
        )
    equipment_ids = [item["equipment_id"] for item in active_items]
    placeholders = ",".join(("?" for _ in equipment_ids))
    queries.return_all_mission_items_2(
        cursor, (return_date.strip(), return_notes.strip(), mission_id)
    )
    queries.return_all_mission_items_3(cursor, equipment_ids, placeholders)
    queries.return_all_mission_items_4(
        cursor, (datetime.now().isoformat(timespec="seconds"), mission_id)
    )
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url(
            f"/missions/{mission_id}", "Όλος ο εξοπλισμός της αποστολής επέστρεψε στα ράφια."
        ),
        status_code=303,
    )


def delete_history_movement(loan_id: int):
    connection = get_connection(write=True)
    cursor = connection.cursor()
    loan = queries.delete_history_movement_1(cursor, (loan_id,)).fetchone()
    if loan is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Η κίνηση δεν βρέθηκε.")
    equipment_id = loan["equipment_id"]
    queries.delete_history_movement_2(cursor, (loan_id,))
    active_count = queries.delete_history_movement_3(cursor, (equipment_id,)).fetchone()[0]
    if active_count == 0:
        queries.delete_history_movement_4(cursor, (equipment_id,))
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url("/history", "Η κίνηση διαγράφηκε από το ιστορικό."), status_code=303
    )
