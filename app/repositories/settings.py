"""Parameterized MySQL queries executed through SQLAlchemy Core."""


def get_settings_1(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM app_settings
        WHERE id = 1
    """,
        parameters,
    )


def edit_headquarters_1(connection, parameters):
    return connection.execute(
        """
        UPDATE app_settings
        SET headquarters_name = ?, headquarters_address = ?,
            headquarters_latitude = ?, headquarters_longitude = ?
        WHERE id = 1
    """,
        parameters,
    )


def settings_page_1(connection, parameters):
    return connection.execute(
        """
            SELECT id, username, full_name, role, active, created_at, last_login
            FROM users
            ORDER BY active DESC, role ASC, LOWER(full_name) ASC
        """,
        parameters,
    )


def settings_page_2(connection, parameters):
    return connection.execute(
        """
            SELECT username, full_name, role, action, path, created_at
            FROM audit_log
            ORDER BY id DESC
            LIMIT 40
        """,
        parameters,
    )


def update_settings_1(connection, parameters):
    return connection.execute(
        """
        UPDATE app_settings

        SET
            application_name = ?,
            library_name = ?,
            organization_name = ?,
            default_unit = ?

        WHERE id = 1
    """,
        parameters,
    )


def export_equipment_filtered_1(connection, parameters, query):
    return connection.execute(query, parameters)


EXPORT_EQUIPMENT_FILTERED_SQL_1 = """
        SELECT
            description,
            manufacturer,
            model,
            serial_number,
            dei_registry_number,
            tem_internal_code,
            category,
            status,
            location,
            dexion,
            shelf,
            storage_column,
            quantity
        FROM equipment
    """

EXPORT_EQUIPMENT_FILTERED_SQL_2 = """
            WHERE category = ?
        """

EXPORT_EQUIPMENT_FILTERED_SQL_3 = """
        ORDER BY description ASC
    """
