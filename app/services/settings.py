from fastapi import Request, Form, HTTPException
from fastapi.responses import RedirectResponse, FileResponse, Response
from datetime import datetime
import zipfile
import csv
import io
from app.core.config import BASE_DIR, UPLOADS_PATH, BACKUPS_PATH, settings as config
from app.db.session import get_connection
from app.core.templating import templates
import os
import subprocess
from sqlalchemy.engine import make_url
import uuid
from app.core.presentation import parse_optional_coordinate, toast_redirect_url
from app.repositories import settings as queries


def get_settings():
    connection = get_connection()
    cursor = connection.cursor()
    settings = queries.get_settings_1(cursor, ()).fetchone()
    connection.close()
    return settings


def edit_headquarters(
    headquarters_name: str = Form(...),
    headquarters_address: str = Form(""),
    headquarters_latitude: str = Form(""),
    headquarters_longitude: str = Form(""),
):
    headquarters_name = headquarters_name.strip()
    headquarters_address = headquarters_address.strip()
    if not headquarters_name:
        raise HTTPException(status_code=400, detail="Η ονομασία της έδρας είναι υποχρεωτική.")
    latitude_value = parse_optional_coordinate(headquarters_latitude, -90, 90, "Latitude Έδρας")
    longitude_value = parse_optional_coordinate(
        headquarters_longitude, -180, 180, "Longitude Έδρας"
    )
    connection = get_connection(write=True)
    cursor = connection.cursor()
    queries.edit_headquarters_1(
        cursor, (headquarters_name, headquarters_address, latitude_value, longitude_value)
    )
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url(
            "/teams?section=headquarters", "Τα στοιχεία της έδρας ενημερώθηκαν."
        ),
        status_code=303,
    )


def settings_page(request: Request):
    settings = get_settings()
    connection = get_connection()
    try:
        users = queries.settings_page_1(connection, ()).fetchall()
        audit_rows = queries.settings_page_2(connection, ()).fetchall()
    finally:
        connection.close()
    return templates.TemplateResponse(
        request=request,
        name="settings.html",
        context={
            "settings": settings,
            "users": users,
            "audit_rows": audit_rows,
            "current_user": request.state.current_user,
        },
    )


def update_settings(
    application_name: str = Form(...),
    library_name: str = Form(""),
    organization_name: str = Form(""),
    default_unit: str = Form(""),
):
    connection = get_connection(write=True)
    cursor = connection.cursor()
    queries.update_settings_1(
        cursor,
        (
            application_name.strip(),
            library_name.strip(),
            organization_name.strip(),
            default_unit.strip(),
        ),
    )
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url("/settings", "Οι ρυθμίσεις αποθηκεύτηκαν."), status_code=303
    )


def download_backup():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_" + uuid.uuid4().hex[:8]
    backup_name = "Equipment_Library_Backup_" + timestamp + ".zip"
    backup_path = BACKUPS_PATH / backup_name
    database_snapshot = BACKUPS_PATH / ("equipment_" + timestamp + ".sql")
    database_url = make_url(config.database_url)
    environment = dict(os.environ, MYSQL_PWD=database_url.password or "")
    try:
        subprocess.run(
            ["mariadb-dump", "--host", database_url.host or "db",
             "--port", str(database_url.port or 3306),
             "--user", database_url.username or "equipment",
             "--single-transaction", "--skip-lock-tables", "--no-tablespaces",
             "--skip-ssl", "--result-file", str(database_snapshot),
             database_url.database or "equipment"],
            env=environment, check=True, capture_output=True,
        )
        with zipfile.ZipFile(backup_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.write(database_snapshot, arcname="data/equipment.sql")
            if UPLOADS_PATH.exists():
                for file_path in UPLOADS_PATH.rglob("*"):
                    if not file_path.is_file():
                        continue
                    relative_path = file_path.relative_to(BASE_DIR)
                    archive.write(file_path, arcname=str(relative_path))
            backup_info = f"Equipment Library Manager Backup\nΗμερομηνία δημιουργίας: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n\nΠεριεχόμενα:\n- data/equipment.sql\n- uploads/equipment\n- uploads/locations\n- uploads/documents\n"
            archive.writestr("backup_info.txt", backup_info)
    finally:
        if database_snapshot.exists():
            try:
                database_snapshot.unlink()
            except OSError:
                pass
    return FileResponse(path=backup_path, media_type="application/zip", filename=backup_name)


def export_equipment_filtered(category: str = ""):
    connection = get_connection()
    cursor = connection.cursor()
    query = queries.EXPORT_EQUIPMENT_FILTERED_SQL_1
    params = []
    if category:
        query += queries.EXPORT_EQUIPMENT_FILTERED_SQL_2
        params.append(category)
    query += queries.EXPORT_EQUIPMENT_FILTERED_SQL_3
    rows = queries.export_equipment_filtered_1(cursor, params, query).fetchall()
    connection.close()
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow(
        [
            "Περιγραφή",
            "Κατασκευαστής",
            "Μοντέλο",
            "Serial Number",
            "Αρ. Μητρώου ΔΕΗ",
            "Κωδικός ΤΕΜ",
            "Κατηγορία",
            "Κατάσταση",
            "Τοποθεσία",
            "Dexion",
            "Ράφι",
            "Στήλη",
            "Ποσότητα",
        ]
    )
    for row in rows:
        writer.writerow(
            [
                row["description"] or "",
                row["manufacturer"] or "",
                row["model"] or "",
                row["serial_number"] or "",
                row["dei_registry_number"] or "",
                row["tem_internal_code"] or "",
                row["category"] or "",
                row["status"] or "",
                row["location"] or "",
                row["dexion"] or "",
                row["shelf"] or "",
                row["storage_column"] or "",
                row["quantity"] or "",
            ]
        )
    csv_bytes = ("\ufeff" + output.getvalue()).encode("utf-8")
    safe_suffix = (
        "all" if not category else category.replace(" ", "_").replace("/", "_").replace("\\", "_")
    )
    filename = "equipment_" + safe_suffix + "_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".csv"
    return Response(
        content=csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
