from fastapi import Request, Form, File, UploadFile, HTTPException
from fastapi.responses import RedirectResponse
from datetime import datetime
from app.core.config import EQUIPMENT_PHOTOS_PATH, LOCATION_PHOTOS_PATH, DOCUMENTS_PATH
from app.db.session import get_connection, IntegrityError
from app.core.templating import templates
from app.core.presentation import build_location_text, format_date, toast_redirect_url
from app.services.files import save_pdf, save_photo
from app.services.settings import get_settings
from app.repositories import equipment as queries


def equipment_list(
    request: Request,
    q: str = "",
    category: str = "",
    manufacturer: str = "",
    equipment_status: str = "",
    location_filter: str = "",
    selected_id: int | None = None,
    page: int = 1,
):
    connection = get_connection()
    cursor = connection.cursor()
    page = max(1, page)
    per_page = 25
    where_clauses = []
    parameters = []
    if q:
        search_term = f"%{q}%"
        where_clauses.append(queries.EQUIPMENT_LIST_SQL_1)
        parameters.extend([search_term] * 12)
    if category:
        where_clauses.append(queries.EQUIPMENT_LIST_SQL_2)
        parameters.append(category)
    if manufacturer:
        where_clauses.append(queries.EQUIPMENT_LIST_SQL_3)
        parameters.append(manufacturer)
    if equipment_status:
        where_clauses.append(queries.EQUIPMENT_LIST_SQL_4)
        parameters.append(equipment_status)
    if location_filter:
        where_clauses.append(queries.EQUIPMENT_LIST_SQL_5)
        parameters.append(location_filter)
    where_sql = ""
    if where_clauses:
        where_sql = queries.EQUIPMENT_LIST_SQL_6 + queries.EQUIPMENT_LIST_SQL_7.join(where_clauses)
    total_count = queries.equipment_list_1(cursor, parameters, where_sql).fetchone()[0]
    total_pages = max(1, (total_count + per_page - 1) // per_page)
    page = min(page, total_pages)
    offset = (page - 1) * per_page
    equipment = queries.equipment_list_2(
        cursor, parameters + [per_page, offset], where_sql
    ).fetchall()
    categories = queries.equipment_list_3(cursor, ()).fetchall()
    manufacturers = queries.equipment_list_4(cursor, ()).fetchall()
    statuses = queries.equipment_list_5(cursor, ()).fetchall()
    locations = queries.equipment_list_6(cursor, ()).fetchall()
    visible_ids = {item["id"] for item in equipment}
    if selected_id not in visible_ids:
        selected_id = equipment[0]["id"] if equipment else None
    connection.close()
    return templates.TemplateResponse(
        request=request,
        name="equipment.html",
        context={
            "equipment": equipment,
            "q": q,
            "category": category,
            "manufacturer": manufacturer,
            "equipment_status": equipment_status,
            "location_filter": location_filter,
            "categories": categories,
            "manufacturers": manufacturers,
            "statuses": statuses,
            "locations": locations,
            "selected_id": selected_id,
            "page": page,
            "per_page": per_page,
            "total_count": total_count,
            "total_pages": total_pages,
            "settings": get_settings(),
        },
    )


def equipment_panel_data(equipment_id: int):
    connection = get_connection()
    cursor = connection.cursor()
    item = queries.equipment_panel_data_1(cursor, (equipment_id,)).fetchone()
    if item is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Ο εξοπλισμός δεν βρέθηκε.")
    documents = queries.equipment_panel_data_2(cursor, (equipment_id,)).fetchall()
    loans = queries.equipment_panel_data_3(cursor, (equipment_id,)).fetchall()
    movement_history = []
    for loan in loans:
        movement_history.append(
            {
                "loan_id": loan["id"],
                "type": "Χρέωση",
                "date": format_date(loan["checkout_date"]),
                "team": loan["borrower_name"] or "",
                "unit": loan["borrower_unit"] or "",
                "notes": loan["checkout_notes"] or "",
            }
        )
        if loan["return_date"]:
            movement_history.append(
                {
                    "loan_id": loan["id"],
                    "type": "Επιστροφή",
                    "date": format_date(loan["return_date"]),
                    "team": loan["borrower_name"] or "",
                    "unit": loan["borrower_unit"] or "",
                    "notes": loan["return_notes"] or "",
                }
            )
    result = dict(item)
    result["documents"] = [
        {
            "id": document["id"],
            "name": document["original_name"],
            "url": "/uploads/documents/" + document["stored_name"],
            "uploaded_at": document["uploaded_at"],
        }
        for document in documents
    ]
    result["history"] = movement_history[:8]
    result["equipment_photo_url"] = (
        "/uploads/equipment/" + item["equipment_photo"] if item["equipment_photo"] else ""
    )
    result["location_photo_url"] = (
        "/uploads/locations/" + item["location_photo"] if item["location_photo"] else ""
    )
    alternative_rows = queries.equipment_panel_data_4(cursor, (equipment_id,)).fetchall()
    result["alternatives"] = [
        {
            "id": alt["id"],
            "code": alt["code"],
            "description": alt["description"],
            "manufacturer": alt["manufacturer"],
            "model": alt["model"],
            "status": alt["status"],
            "dei_registry_number": alt["dei_registry_number"],
            "tem_internal_code": alt["tem_internal_code"],
        }
        for alt in alternative_rows
    ]
    connection.close()
    return result


def upload_equipment_document(equipment_id: int, document: UploadFile = File(...)):
    connection = get_connection(write=True)
    cursor = connection.cursor()
    item = queries.upload_equipment_document_1(cursor, (equipment_id,)).fetchone()
    if item is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Ο εξοπλισμός δεν βρέθηκε.")
    stored_name = save_pdf(document, DOCUMENTS_PATH, f"equipment_{equipment_id}")
    queries.upload_equipment_document_2(
        cursor,
        (
            equipment_id,
            document.filename,
            stored_name,
            datetime.now().isoformat(timespec="seconds"),
        ),
    )
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url(f"/equipment/{equipment_id}/edit", "Το PDF ανέβηκε επιτυχώς."),
        status_code=303,
    )


def delete_equipment_document(equipment_id: int, document_id: int):
    connection = get_connection(write=True)
    cursor = connection.cursor()
    document = queries.delete_equipment_document_1(cursor, (document_id, equipment_id)).fetchone()
    if document is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Το PDF δεν βρέθηκε.")
    queries.delete_equipment_document_2(cursor, (document_id, equipment_id))
    connection.commit()
    connection.close()
    file_path = DOCUMENTS_PATH / document["stored_name"]
    if file_path.exists():
        try:
            file_path.unlink()
        except OSError:
            pass
    return RedirectResponse(
        url=toast_redirect_url(f"/equipment/{equipment_id}/edit", "Το PDF διαγράφηκε."),
        status_code=303,
    )


def new_equipment_page(request: Request):
    connection = get_connection()
    cursor = connection.cursor()
    storage_locations = queries.new_equipment_page_1(cursor, ()).fetchall()
    categories = queries.new_equipment_page_2(cursor, ()).fetchall()
    connection.close()
    return templates.TemplateResponse(
        request=request,
        name="equipment_new.html",
        context={
            "storage_locations": storage_locations,
            "categories": categories,
            "settings": get_settings(),
        },
    )


def create_equipment(
    code: str = Form(...),
    description: str = Form(...),
    category: str = Form(""),
    manufacturer: str = Form(""),
    model: str = Form(""),
    serial_number: str = Form(""),
    dei_registry_number: str = Form(""),
    tem_internal_code: str = Form(""),
    dexion: str = Form(""),
    shelf: str = Form(""),
    storage_column: str = Form(""),
    status: str = Form("Διαθέσιμο"),
    quantity: int = Form(1),
    notes: str = Form(""),
    equipment_photo: UploadFile | None = File(None),
    location_photo: UploadFile | None = File(None),
):
    equipment_photo_name = save_photo(equipment_photo, EQUIPMENT_PHOTOS_PATH, "equipment")
    location_photo_name = save_photo(location_photo, LOCATION_PHOTOS_PATH, "location")
    location = build_location_text(dexion, shelf, storage_column)
    connection = get_connection(write=True)
    cursor = connection.cursor()
    queries.create_equipment_1(
        cursor,
        (
            code.strip(),
            description.strip(),
            category.strip(),
            manufacturer.strip(),
            model.strip(),
            serial_number.strip(),
            dei_registry_number.strip(),
            tem_internal_code.strip(),
            dexion.strip(),
            shelf.strip(),
            storage_column.strip(),
            location,
            status.strip(),
            max(1, quantity),
            notes.strip(),
            equipment_photo_name,
            location_photo_name,
        ),
    )
    connection.commit()
    new_id = cursor.lastrowid
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url(f"/equipment/{new_id}", "Ο εξοπλισμός καταχωρίστηκε επιτυχώς."),
        status_code=303,
    )


def checkout_equipment(
    equipment_id: int,
    borrower_name: str = Form(...),
    borrower_unit: str = Form(""),
    checkout_date: str = Form(...),
    expected_return_date: str = Form(""),
    checkout_notes: str = Form(""),
):
    connection = get_connection(write=True)
    cursor = connection.cursor()
    item = queries.checkout_equipment_1(cursor, (equipment_id,)).fetchone()
    if item is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Ο εξοπλισμός δεν βρέθηκε.")
    if item["status"] != "Διαθέσιμο":
        connection.close()
        raise HTTPException(status_code=400, detail="Ο εξοπλισμός δεν είναι διαθέσιμος για χρέωση.")
    queries.checkout_equipment_2(
        cursor,
        (
            equipment_id,
            borrower_name.strip(),
            borrower_unit.strip(),
            checkout_date.strip(),
            expected_return_date.strip(),
            checkout_notes.strip(),
            datetime.now().isoformat(timespec="seconds"),
        ),
    )
    queries.checkout_equipment_3(cursor, (equipment_id,))
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url("/checkout-return", "Η χρέωση ολοκληρώθηκε επιτυχώς."),
        status_code=303,
    )


def delete_equipment(equipment_id: int):
    connection = get_connection(write=True)
    cursor = connection.cursor()
    item = queries.delete_equipment_1(cursor, (equipment_id,)).fetchone()
    if item is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Ο εξοπλισμός δεν βρέθηκε.")
    documents = queries.delete_equipment_2(cursor, (equipment_id,)).fetchall()
    queries.delete_equipment_3(cursor, (equipment_id,))
    queries.delete_equipment_4(cursor, (equipment_id,))
    queries.delete_equipment_5(cursor, (equipment_id,))
    connection.commit()
    connection.close()
    for document in documents:
        document_path = DOCUMENTS_PATH / document["stored_name"]
        if document_path.exists():
            try:
                document_path.unlink()
            except OSError:
                pass
    if item["equipment_photo"]:
        equipment_photo_path = EQUIPMENT_PHOTOS_PATH / item["equipment_photo"]
        if equipment_photo_path.exists():
            try:
                equipment_photo_path.unlink()
            except OSError:
                pass
    if item["location_photo"]:
        location_photo_path = LOCATION_PHOTOS_PATH / item["location_photo"]
        if location_photo_path.exists():
            try:
                location_photo_path.unlink()
            except OSError:
                pass
    return RedirectResponse(
        url=toast_redirect_url("/equipment", "Ο εξοπλισμός διαγράφηκε."), status_code=303
    )


def add_equipment_alternative(equipment_id: int, identifier: str = Form(...)):
    key = identifier.strip()
    if not key:
        return RedirectResponse(
            url=toast_redirect_url(
                f"/equipment/{equipment_id}#alternatives",
                "Συμπληρώστε Κωδικό, ΑΜ ΔΕΗ ή Κωδικό ΤΕΜ.",
                "error",
            ),
            status_code=303,
        )
    connection = get_connection(write=True)
    cursor = connection.cursor()
    source = queries.add_equipment_alternative_1(cursor, (equipment_id,)).fetchone()
    if source is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Ο εξοπλισμός δεν βρέθηκε.")
    target = queries.add_equipment_alternative_2(cursor, (key, key, key)).fetchone()
    if target is None:
        connection.close()
        return RedirectResponse(
            url=toast_redirect_url(
                f"/equipment/{equipment_id}#alternatives",
                "Δεν βρέθηκε εξοπλισμός με αυτό το αναγνωριστικό.",
                "error",
            ),
            status_code=303,
        )
    if target["id"] == equipment_id:
        connection.close()
        return RedirectResponse(
            url=toast_redirect_url(
                f"/equipment/{equipment_id}#alternatives",
                "Ο εξοπλισμός δεν μπορεί να είναι εναλλακτική του εαυτού του.",
                "error",
            ),
            status_code=303,
        )
    reverse = queries.add_equipment_alternative_3(cursor, (target["id"], equipment_id)).fetchone()
    if reverse:
        connection.close()
        return RedirectResponse(
            url=toast_redirect_url(
                f"/equipment/{equipment_id}#alternatives",
                "Δεν επιτρέπεται άμεσος κύκλος εναλλακτικών A ↔ B.",
                "error",
            ),
            status_code=303,
        )
    priority = queries.add_equipment_alternative_4(cursor, (equipment_id,)).fetchone()[0]
    try:
        queries.add_equipment_alternative_5(
            cursor,
            (equipment_id, target["id"], priority, datetime.now().isoformat(timespec="seconds")),
        )
        connection.commit()
        message = f"Προστέθηκε εναλλακτική: {target['code']} — {target['description']}"
    except IntegrityError:
        message = "Η συγκεκριμένη εναλλακτική είναι ήδη καταχωρισμένη."
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url(f"/equipment/{equipment_id}#alternatives", message), status_code=303
    )


def delete_equipment_alternative(equipment_id: int, relation_id: int):
    connection = get_connection(write=True)
    queries.delete_equipment_alternative_1(connection, (relation_id, equipment_id))
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url(
            f"/equipment/{equipment_id}#alternatives", "Η εναλλακτική αφαιρέθηκε."
        ),
        status_code=303,
    )


def equipment_detail(request: Request, equipment_id: int):
    connection = get_connection()
    cursor = connection.cursor()
    item = queries.equipment_detail_1(cursor, (equipment_id,)).fetchone()
    if item is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Ο εξοπλισμός δεν βρέθηκε.")
    documents = queries.equipment_detail_2(cursor, (equipment_id,)).fetchall()
    alternatives = queries.equipment_detail_3(cursor, (equipment_id,)).fetchall()
    loans = queries.equipment_detail_4(cursor, (equipment_id,)).fetchall()
    movement_history = []
    for loan in loans:
        movement_history.append(
            {
                "type": "Χρέωση",
                "date": format_date(loan["checkout_date"]),
                "team": loan["borrower_name"] or "",
                "unit": loan["borrower_unit"] or "",
                "notes": loan["checkout_notes"] or "",
            }
        )
        if loan["return_date"]:
            movement_history.append(
                {
                    "type": "Επιστροφή",
                    "date": format_date(loan["return_date"]),
                    "team": loan["borrower_name"] or "",
                    "unit": loan["borrower_unit"] or "",
                    "notes": loan["return_notes"] or "",
                }
            )
    connection.close()
    return templates.TemplateResponse(
        request=request,
        name="equipment_detail.html",
        context={
            "item": item,
            "documents": documents,
            "movement_history": movement_history,
            "alternatives": alternatives,
            "settings": get_settings(),
        },
    )


def equipment_edit_page(request: Request, equipment_id: int):
    connection = get_connection()
    cursor = connection.cursor()
    item = queries.equipment_edit_page_1(cursor, (equipment_id,)).fetchone()
    storage_locations = queries.equipment_edit_page_2(cursor, ()).fetchall()
    categories = queries.equipment_edit_page_3(cursor, ()).fetchall()
    documents = queries.equipment_edit_page_4(cursor, (equipment_id,)).fetchall()
    connection.close()
    if item is None:
        raise HTTPException(status_code=404, detail="Ο εξοπλισμός δεν βρέθηκε.")
    return templates.TemplateResponse(
        request=request,
        name="equipment_edit.html",
        context={
            "item": item,
            "storage_locations": storage_locations,
            "categories": categories,
            "documents": documents,
            "settings": get_settings(),
        },
    )


def update_equipment(
    equipment_id: int,
    code: str = Form(...),
    description: str = Form(...),
    category: str = Form(""),
    manufacturer: str = Form(""),
    model: str = Form(""),
    serial_number: str = Form(""),
    dei_registry_number: str = Form(""),
    tem_internal_code: str = Form(""),
    dexion: str = Form(""),
    shelf: str = Form(""),
    storage_column: str = Form(""),
    status: str = Form("Διαθέσιμο"),
    quantity: int = Form(1),
    notes: str = Form(""),
    equipment_photo: UploadFile | None = File(None),
    location_photo: UploadFile | None = File(None),
):
    connection = get_connection(write=True)
    cursor = connection.cursor()
    existing = queries.update_equipment_1(cursor, (equipment_id,)).fetchone()
    if existing is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Ο εξοπλισμός δεν βρέθηκε.")
    equipment_photo_name = existing["equipment_photo"]
    location_photo_name = existing["location_photo"]
    if equipment_photo is not None and equipment_photo.filename:
        equipment_photo_name = save_photo(equipment_photo, EQUIPMENT_PHOTOS_PATH, "equipment")
    if location_photo is not None and location_photo.filename:
        location_photo_name = save_photo(location_photo, LOCATION_PHOTOS_PATH, "location")
    location = build_location_text(dexion, shelf, storage_column)
    queries.update_equipment_2(
        cursor,
        (
            code.strip(),
            description.strip(),
            category.strip(),
            manufacturer.strip(),
            model.strip(),
            serial_number.strip(),
            dei_registry_number.strip(),
            tem_internal_code.strip(),
            dexion.strip(),
            shelf.strip(),
            storage_column.strip(),
            location,
            status.strip(),
            max(1, quantity),
            notes.strip(),
            equipment_photo_name,
            location_photo_name,
            equipment_id,
        ),
    )
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url(f"/equipment/{equipment_id}", "Οι αλλαγές αποθηκεύτηκαν επιτυχώς."),
        status_code=303,
    )
