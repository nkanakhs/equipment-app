"""Parameterized MySQL queries executed through SQLAlchemy Core."""


def teams_page_1(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM measurement_teams
        ORDER BY name ASC
    """,
        parameters,
    )


def teams_page_2(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM mission_vehicles
        ORDER BY model ASC, license_plate ASC
    """,
        parameters,
    )


def teams_page_3(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM mission_destinations
        ORDER BY name ASC
    """,
        parameters,
    )


def create_team_1(connection, parameters):
    return connection.execute(
        """
        SELECT id
        FROM measurement_teams
        WHERE LOWER(name) = LOWER(?)
    """,
        parameters,
    )


def create_team_2(connection, parameters):
    return connection.execute(
        """
        INSERT INTO measurement_teams (
            name,
            description,
            active
        )
        VALUES (?, ?, 1)
    """,
        parameters,
    )


def edit_team_1(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM measurement_teams
        WHERE id = ?
    """,
        parameters,
    )


def edit_team_2(connection, parameters):
    return connection.execute(
        """
        SELECT id
        FROM measurement_teams
        WHERE LOWER(name) = LOWER(?)
          AND id <> ?
    """,
        parameters,
    )


def edit_team_3(connection, parameters):
    return connection.execute(
        """
        UPDATE measurement_teams

        SET
            name = ?,
            description = ?,
            active = ?

        WHERE id = ?
    """,
        parameters,
    )


def edit_team_4(connection, parameters):
    return connection.execute(
        """
            UPDATE loans
            SET borrower_name = ?
            WHERE borrower_name = ?
        """,
        parameters,
    )


def delete_team_1(connection, parameters):
    return connection.execute(
        """
        DELETE FROM measurement_teams
        WHERE id = ?
    """,
        parameters,
    )


def create_mission_vehicle_1(connection, parameters):
    return connection.execute(
        """
        SELECT id
        FROM mission_vehicles
        WHERE LOWER(license_plate) = LOWER(?)
    """,
        parameters,
    )


def create_mission_vehicle_2(connection, parameters):
    return connection.execute(
        """
        INSERT INTO mission_vehicles (
            model,
            license_plate,
            active
        )
        VALUES (?, ?, 1)
    """,
        parameters,
    )


def delete_mission_vehicle_1(connection, parameters):
    return connection.execute(
        """
        DELETE FROM mission_vehicles
        WHERE id = ?
    """,
        parameters,
    )


def create_mission_destination_1(connection, parameters):
    return connection.execute(
        """
        SELECT id FROM mission_destinations
        WHERE LOWER(name) = LOWER(?)
           OR (? <> '' AND station_code = ?)
    """,
        parameters,
    )


def create_mission_destination_2(connection, parameters):
    return connection.execute(
        """
        INSERT INTO mission_destinations (
            station_code, name, category, energy_source, area_system,
            address, latitude, longitude, coordinate_accuracy,
            operational_status, notes,
            is_location_verified, show_on_map, active
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        parameters,
    )


def edit_mission_destination_1(connection, parameters):
    return connection.execute("SELECT * FROM mission_destinations WHERE id = ?", parameters)


def edit_mission_destination_2(connection, parameters):
    return connection.execute(
        """
        SELECT id FROM mission_destinations
        WHERE id <> ?
          AND (LOWER(name) = LOWER(?) OR (? <> '' AND station_code = ?))
    """,
        parameters,
    )


def edit_mission_destination_3(connection, parameters):
    return connection.execute(
        """
        UPDATE mission_destinations
        SET station_code=?, name=?, category=?, energy_source=?, area_system=?,
            address=?, latitude=?, longitude=?, coordinate_accuracy=?,
            operational_status=?, notes=?,
            is_location_verified=?, show_on_map=?, active=?
        WHERE id=?
    """,
        parameters,
    )


def edit_mission_destination_4(connection, parameters):
    return connection.execute(
        "UPDATE field_missions SET destination = ? WHERE destination = ?", parameters
    )


def delete_mission_destination_1(connection, parameters):
    return connection.execute(
        """
        DELETE FROM mission_destinations
        WHERE id = ?
    """,
        parameters,
    )
