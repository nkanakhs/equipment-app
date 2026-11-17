from fastapi import HTTPException
from pathlib import Path
import shutil
import uuid


def save_photo(uploaded_file, target_folder, prefix):
    if uploaded_file is None:
        return None
    if not uploaded_file.filename:
        return None
    extension = Path(uploaded_file.filename).suffix.lower()
    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    if extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Επιτρέπονται μόνο JPG, JPEG, PNG και WEBP.")
    filename = f"{prefix}_{uuid.uuid4().hex}{extension}"
    file_path = target_folder / filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)
    return filename


def save_pdf(uploaded_file, target_folder, prefix):
    if uploaded_file is None:
        return None
    if not uploaded_file.filename:
        return None
    extension = Path(uploaded_file.filename).suffix.lower()
    if extension != ".pdf":
        raise HTTPException(status_code=400, detail="Επιτρέπονται μόνο αρχεία PDF.")
    filename = f"{prefix}_{uuid.uuid4().hex}{extension}"
    file_path = target_folder / filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)
    return filename
