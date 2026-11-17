from fastapi import Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from app.db.session import get_connection
from app.core.templating import templates
from app.core.presentation import toast_redirect_url
from app.services.settings import get_settings
from app.repositories import categories as queries


def categories_page(request: Request):
    connection = get_connection()
    cursor = connection.cursor()
    categories = queries.categories_page_1(cursor, ()).fetchall()
    connection.close()
    return templates.TemplateResponse(
        request=request,
        name="categories.html",
        context={"categories": categories, "settings": get_settings()},
    )


def create_category(name: str = Form(...), description: str = Form("")):
    name = name.strip()
    description = description.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Η ονομασία της κατηγορίας είναι υποχρεωτική.")
    connection = get_connection(write=True)
    cursor = connection.cursor()
    existing = queries.create_category_1(cursor, (name,)).fetchone()
    if existing is not None:
        connection.close()
        raise HTTPException(status_code=400, detail="Υπάρχει ήδη κατηγορία με αυτή την ονομασία.")
    queries.create_category_2(cursor, (name, description))
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url("/categories", "Η κατηγορία δημιουργήθηκε επιτυχώς."),
        status_code=303,
    )


def edit_category(category_id: int, name: str = Form(...), description: str = Form("")):
    name = name.strip()
    description = description.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Η ονομασία της κατηγορίας είναι υποχρεωτική.")
    connection = get_connection(write=True)
    cursor = connection.cursor()
    category = queries.edit_category_1(cursor, (category_id,)).fetchone()
    if category is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Η κατηγορία δεν βρέθηκε.")
    duplicate = queries.edit_category_2(cursor, (name, category_id)).fetchone()
    if duplicate is not None:
        connection.close()
        raise HTTPException(
            status_code=400, detail="Υπάρχει ήδη άλλη κατηγορία με αυτή την ονομασία."
        )
    old_name = category["name"]
    queries.edit_category_3(cursor, (name, description, category_id))
    if old_name != name:
        queries.edit_category_4(cursor, (name, old_name))
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url("/categories", "Η κατηγορία ενημερώθηκε."), status_code=303
    )


def delete_category(category_id: int):
    connection = get_connection(write=True)
    cursor = connection.cursor()
    category = queries.delete_category_1(cursor, (category_id,)).fetchone()
    if category is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Η κατηγορία δεν βρέθηκε.")
    used_count = queries.delete_category_2(cursor, (category["name"],)).fetchone()[0]
    if used_count > 0:
        connection.close()
        raise HTTPException(
            status_code=400,
            detail="Η κατηγορία χρησιμοποιείται από καταχωρισμένο εξοπλισμό και δεν μπορεί να διαγραφεί.",
        )
    queries.delete_category_3(cursor, (category_id,))
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url("/categories", "Η κατηγορία διαγράφηκε."), status_code=303
    )
