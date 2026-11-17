"""Parameterized MySQL queries executed through SQLAlchemy Core."""


def locations_page_1(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM storage_locations
        ORDER BY
            dexion,
            shelf,
            storage_column
    """,
        parameters,
    )


def create_location_1(connection, parameters):
    return connection.execute(
        """
        SELECT id
        FROM storage_locations

        WHERE LOWER(dexion) = LOWER(?)
          AND LOWER(shelf) = LOWER(?)
          AND LOWER(storage_column) = LOWER(?)
    """,
        parameters,
    )


def create_location_2(connection, parameters):
    return connection.execute(
        """
        INSERT INTO storage_locations (

            dexion,
            shelf,
            storage_column,
            description,
            active

        )

        VALUES (?, ?, ?, ?, 1)
    """,
        parameters,
    )


def edit_location_1(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM storage_locations
        WHERE id = ?
    """,
        parameters,
    )


def edit_location_2(connection, parameters):
    return connection.execute(
        """
        SELECT id
        FROM storage_locations
        WHERE LOWER(dexion) = LOWER(?)
          AND LOWER(shelf) = LOWER(?)
          AND LOWER(storage_column) = LOWER(?)
          AND id != ?
    """,
        parameters,
    )


def edit_location_3(connection, parameters):
    return connection.execute(
        """
        UPDATE storage_locations
        SET
            dexion = ?,
            shelf = ?,
            storage_column = ?,
            description = ?
        WHERE id = ?
    """,
        parameters,
    )


def edit_location_4(connection, parameters):
    return connection.execute(
        """
        UPDATE equipment
        SET
            dexion = ?,
            shelf = ?,
            storage_column = ?,
            location = ?
        WHERE COALESCE(dexion, '') = ?
          AND COALESCE(shelf, '') = ?
          AND COALESCE(storage_column, '') = ?
    """,
        parameters,
    )


def delete_location_1(connection, parameters):
    return connection.execute(
        """
        DELETE FROM storage_locations
        WHERE id = ?
    """,
        parameters,
    )
