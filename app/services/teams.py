from fastapi import Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from app.db.session import get_connection
from app.core.templating import templates
from app.core.presentation import parse_optional_coordinate, toast_redirect_url
from app.services.settings import get_settings
from app.repositories import teams as queries


def teams_page(request: Request, section: str = ""):
    connection = get_connection()
    cursor = connection.cursor()
    teams = queries.teams_page_1(cursor, ()).fetchall()
    vehicles = queries.teams_page_2(cursor, ()).fetchall()
    destinations = queries.teams_page_3(cursor, ()).fetchall()
    connection.close()
    allowed_sections = {"groups", "vehicles", "headquarters", "stations"}
    resource_section = section if section in allowed_sections else ""
    return templates.TemplateResponse(
        request=request,
        name="teams.html",
        context={
            "teams": teams,
            "vehicles": vehicles,
            "destinations": destinations,
            "settings": get_settings(),
            "headquarters": get_settings(),
            "resource_section": resource_section,
        },
    )


def create_team(name: str = Form(...), description: str = Form("")):
    name = name.strip()
    description = description.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Η ονομασία της ομάδας είναι υποχρεωτική.")
    connection = get_connection(write=True)
    cursor = connection.cursor()
    existing = queries.create_team_1(cursor, (name,)).fetchone()
    if existing is not None:
        connection.close()
        raise HTTPException(status_code=400, detail="Υπάρχει ήδη ομάδα με αυτή την ονομασία.")
    queries.create_team_2(cursor, (name, description))
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url("/teams?section=groups", "Η ομάδα δημιουργήθηκε επιτυχώς."),
        status_code=303,
    )


def edit_team(
    team_id: int, name: str = Form(...), description: str = Form(""), active: int = Form(1)
):
    name = name.strip()
    description = description.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Η ονομασία της ομάδας είναι υποχρεωτική.")
    connection = get_connection(write=True)
    cursor = connection.cursor()
    team = queries.edit_team_1(cursor, (team_id,)).fetchone()
    if team is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Η ομάδα δεν βρέθηκε.")
    duplicate = queries.edit_team_2(cursor, (name, team_id)).fetchone()
    if duplicate is not None:
        connection.close()
        raise HTTPException(status_code=400, detail="Υπάρχει ήδη άλλη ομάδα με αυτή την ονομασία.")
    old_name = team["name"]
    queries.edit_team_3(cursor, (name, description, 1 if active == 1 else 0, team_id))
    if old_name != name:
        queries.edit_team_4(cursor, (name, old_name))
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url("/teams?section=groups", "Η ομάδα ενημερώθηκε."), status_code=303
    )


def delete_team(team_id: int):
    connection = get_connection(write=True)
    cursor = connection.cursor()
    queries.delete_team_1(cursor, (team_id,))
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url("/teams?section=groups", "Η ομάδα διαγράφηκε."), status_code=303
    )


def create_mission_vehicle(model: str = Form(...), license_plate: str = Form(...)):
    model = model.strip()
    license_plate = license_plate.strip().upper()
    if not model or not license_plate:
        raise HTTPException(status_code=400, detail="Μοντέλο και πινακίδα είναι υποχρεωτικά.")
    connection = get_connection(write=True)
    cursor = connection.cursor()
    duplicate = queries.create_mission_vehicle_1(cursor, (license_plate,)).fetchone()
    if duplicate is not None:
        connection.close()
        raise HTTPException(status_code=400, detail="Υπάρχει ήδη όχημα με αυτή την πινακίδα.")
    queries.create_mission_vehicle_2(cursor, (model, license_plate))
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url("/teams?section=vehicles", "Το όχημα προστέθηκε."), status_code=303
    )


def delete_mission_vehicle(vehicle_id: int):
    connection = get_connection(write=True)
    cursor = connection.cursor()
    queries.delete_mission_vehicle_1(cursor, (vehicle_id,))
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url("/teams?section=vehicles", "Το όχημα διαγράφηκε."), status_code=303
    )


def create_mission_destination(
    name: str = Form(...),
    station_code: str = Form(""),
    category: str = Form(""),
    energy_source: str = Form(""),
    area_system: str = Form(""),
    address: str = Form(""),
    latitude: str = Form(""),
    longitude: str = Form(""),
    coordinate_accuracy: str = Form(""),
    operational_status: str = Form(""),
    notes: str = Form(""),
    is_location_verified: int = Form(0),
    show_on_map: int = Form(0),
    active: int = Form(1),
):
    name = name.strip()
    station_code = station_code.strip()
    category = category.strip()
    energy_source = energy_source.strip()
    area_system = area_system.strip()
    address = address.strip()
    coordinate_accuracy = coordinate_accuracy.strip()
    operational_status = operational_status.strip()
    notes = notes.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Η ονομασία του σταθμού είναι υποχρεωτική.")
    latitude_value = parse_optional_coordinate(latitude, -90, 90, "Latitude")
    longitude_value = parse_optional_coordinate(longitude, -180, 180, "Longitude")
    connection = get_connection(write=True)
    cursor = connection.cursor()
    duplicate = queries.create_mission_destination_1(
        cursor, (name, station_code, station_code)
    ).fetchone()
    if duplicate is not None:
        connection.close()
        raise HTTPException(status_code=400, detail="Ο σταθμός ή ο κωδικός υπάρχει ήδη.")
    queries.create_mission_destination_2(
        cursor,
        (
            station_code or None,
            name,
            category,
            energy_source,
            area_system,
            address or area_system,
            latitude_value,
            longitude_value,
            coordinate_accuracy,
            operational_status,
            notes,
            1 if is_location_verified == 1 else 0,
            1 if show_on_map == 1 else 0,
            1 if active == 1 else 0,
        ),
    )
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url("/teams?section=stations", "Ο σταθμός προστέθηκε."), status_code=303
    )


def edit_mission_destination(
    destination_id: int,
    name: str = Form(...),
    station_code: str = Form(""),
    category: str = Form(""),
    energy_source: str = Form(""),
    area_system: str = Form(""),
    address: str = Form(""),
    latitude: str = Form(""),
    longitude: str = Form(""),
    coordinate_accuracy: str = Form(""),
    operational_status: str = Form(""),
    notes: str = Form(""),
    is_location_verified: int = Form(0),
    show_on_map: int = Form(0),
    active: int = Form(1),
):
    name = name.strip()
    station_code = station_code.strip()
    category = category.strip()
    energy_source = energy_source.strip()
    area_system = area_system.strip()
    address = address.strip()
    coordinate_accuracy = coordinate_accuracy.strip()
    operational_status = operational_status.strip()
    notes = notes.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Η ονομασία του σταθμού είναι υποχρεωτική.")
    latitude_value = parse_optional_coordinate(latitude, -90, 90, "Latitude")
    longitude_value = parse_optional_coordinate(longitude, -180, 180, "Longitude")
    connection = get_connection(write=True)
    cursor = connection.cursor()
    destination = queries.edit_mission_destination_1(cursor, (destination_id,)).fetchone()
    if destination is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Ο σταθμός δεν βρέθηκε.")
    duplicate = queries.edit_mission_destination_2(
        cursor, (destination_id, name, station_code, station_code)
    ).fetchone()
    if duplicate is not None:
        connection.close()
        raise HTTPException(status_code=400, detail="Υπάρχει ήδη άλλος σταθμός ή κωδικός.")
    old_name = destination["name"]
    queries.edit_mission_destination_3(
        cursor,
        (
            station_code or None,
            name,
            category,
            energy_source,
            area_system,
            address or area_system,
            latitude_value,
            longitude_value,
            coordinate_accuracy,
            operational_status,
            notes,
            1 if is_location_verified == 1 else 0,
            1 if show_on_map == 1 else 0,
            1 if active == 1 else 0,
            destination_id,
        ),
    )
    if old_name != name:
        queries.edit_mission_destination_4(cursor, (name, old_name))
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url("/teams?section=stations", "Τα στοιχεία του σταθμού ενημερώθηκαν."),
        status_code=303,
    )


def delete_mission_destination(destination_id: int):
    connection = get_connection(write=True)
    cursor = connection.cursor()
    queries.delete_mission_destination_1(cursor, (destination_id,))
    connection.commit()
    connection.close()
    return RedirectResponse(
        url=toast_redirect_url("/teams?section=stations", "Ο σταθμός διαγράφηκε."), status_code=303
    )
