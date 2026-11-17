from fastapi import HTTPException
from datetime import datetime


def toast_redirect_url(path: str, message: str, toast_type: str = "success"):
    from urllib.parse import urlencode

    separator = "&" if "?" in path else "?"
    return path + separator + urlencode({"toast": message, "toast_type": toast_type})


def parse_optional_coordinate(value, minimum, maximum, label):
    value = (value or "").strip().replace(",", ".")
    if not value:
        return None
    try:
        number = float(value)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Το πεδίο {label} πρέπει να είναι αριθμός.")
    if number < minimum or number > maximum:
        raise HTTPException(
            status_code=400, detail=f"Το πεδίο {label} είναι εκτός επιτρεπτών ορίων."
        )
    return number


def build_location_text(dexion, shelf, storage_column):
    parts = []
    if dexion.strip():
        parts.append(f"Dexion {dexion.strip()}")
    if shelf.strip():
        parts.append(f"Ράφι {shelf.strip()}")
    if storage_column.strip():
        parts.append(f"Στήλη {storage_column.strip()}")
    return " / ".join(parts)


def format_date(value):
    if value is None:
        return "—"
    value = str(value).strip()
    if not value:
        return "—"
    try:
        date_part = value[:10]
        parsed = datetime.strptime(date_part, "%Y-%m-%d")
        return parsed.strftime("%d-%m-%Y")
    except ValueError:
        return value
