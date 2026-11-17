from fastapi import Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from app.db.session import get_connection
from app.core.templating import templates
from app.core.presentation import build_location_text, toast_redirect_url
from app.services.settings import get_settings
from app.repositories import locations as queries


def locations_page(request: Request):
    connection = get_connection()
    cursor = connection.cursor()
    storage_locations = queries.locations_page_1(cursor, ()).fetchall()
    connection.close()
    return templates.TemplateResponse(
        request=request,
        name="locations.html",
        context={"storage_locations": storage_locations, "settings": get_settings()},
    )


def create_location(
    dexion: str = Form(...),
    shelf: str = Form(...),
    storage_column: str = Form(...),
    description: str = Form(""),
):
    dexion = dexion.strip()
    shelf = shelf.strip()
    storage_column = storage_column.strip()
    description = description.strip()
    if not dexion or not shelf or (not storage_column):
        raise HTTPException(status_code=400, detail="Dexion, Ράφι και Στήλη είναι υποχρεωτικά.")
    connection = get_connection(write=True)
    cursor = connection.cursor()
    existing = queries.create_location_1(cursor, (dexion, shelf, storage_column)).fetchone()
    if existing is not None:
        connection.close()
        raise HTTPException(status_code=400, detail="Η συγκεκριμένη θέση υπάρχει ήδη.")
    queries.create_location_2(cursor, (dexion, shelf, storage_column, description))
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url("/locations", "Η θέση αποθήκευσης δημιουργήθηκε."), status_code=303
    )


def edit_location(
    location_id: int,
    dexion: str = Form(...),
    shelf: str = Form(...),
    storage_column: str = Form(...),
    description: str = Form(""),
):
    dexion = dexion.strip()
    shelf = shelf.strip()
    storage_column = storage_column.strip()
    description = description.strip()
    if not dexion or not shelf or (not storage_column):
        raise HTTPException(status_code=400, detail="Dexion, Ράφι και Στήλη είναι υποχρεωτικά.")
    connection = get_connection(write=True)
    cursor = connection.cursor()
    location = queries.edit_location_1(cursor, (location_id,)).fetchone()
    if location is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Η θέση αποθήκευσης δεν βρέθηκε.")
    duplicate = queries.edit_location_2(
        cursor, (dexion, shelf, storage_column, location_id)
    ).fetchone()
    if duplicate is not None:
        connection.close()
        raise HTTPException(status_code=400, detail="Υπάρχει ήδη άλλη θέση με τα ίδια στοιχεία.")
    old_dexion = location["dexion"]
    old_shelf = location["shelf"]
    old_column = location["storage_column"]
    new_location_text = build_location_text(dexion, shelf, storage_column)
    queries.edit_location_3(cursor, (dexion, shelf, storage_column, description, location_id))
    queries.edit_location_4(
        cursor,
        (
            dexion,
            shelf,
            storage_column,
            new_location_text,
            old_dexion or "",
            old_shelf or "",
            old_column or "",
        ),
    )
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url("/locations", "Η θέση αποθήκευσης ενημερώθηκε."), status_code=303
    )


def delete_location(location_id: int):
    connection = get_connection(write=True)
    cursor = connection.cursor()
    queries.delete_location_1(cursor, (location_id,))
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url("/locations", "Η θέση αποθήκευσης διαγράφηκε."), status_code=303
    )
