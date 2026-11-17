"""Parameterized MySQL queries executed through SQLAlchemy Core."""


def export_selected_history_1(connection, parameters):
    return connection.execute(
        """
                SELECT *
                FROM field_missions
                WHERE id = ?
            """,
        parameters,
    )


def export_selected_history_2(connection, parameters):
    return connection.execute(
        """
                SELECT

                    field_mission_items.status
                        AS mission_item_status,

                    field_mission_items.returned_at
                        AS mission_item_returned_at,

                    equipment.description,
                    equipment.manufacturer,
                    equipment.model,
                    equipment.serial_number,
                    equipment.dei_registry_number,
                    equipment.tem_internal_code

                FROM field_mission_items

                JOIN equipment
                  ON equipment.id = field_mission_items.equipment_id

                WHERE field_mission_items.mission_id = ?

                ORDER BY field_mission_items.id ASC
            """,
        parameters,
    )


def export_selected_history_3(connection, parameters):
    return connection.execute(
        """
                SELECT

                    loans.*,

                    equipment.description,
                    equipment.manufacturer,
                    equipment.model,
                    equipment.serial_number,
                    equipment.dei_registry_number,
                    equipment.tem_internal_code

                FROM loans

                JOIN equipment
                  ON equipment.id = loans.equipment_id

                WHERE loans.id = ?
            """,
        parameters,
    )


def mission_history_page_1(connection, parameters, where_clause):
    return connection.execute(f"SELECT COUNT(*) FROM field_missions {where_clause}", parameters)


def mission_history_page_2(connection, parameters, where_clause):
    return connection.execute(
        f"\n        SELECT\n            field_missions.*,\n            COUNT(field_mission_items.id) AS total_items,\n            COALESCE(\n                SUM(\n                    CASE\n                        WHEN field_mission_items.status = 'Επιστράφηκε'\n                        THEN 1\n                        ELSE 0\n                    END\n                ),\n                0\n            ) AS returned_items,\n            COALESCE(\n                SUM(\n                    CASE\n                        WHEN field_mission_items.status = 'Σε Αποστολή'\n                        THEN 1\n                        ELSE 0\n                    END\n                ),\n                0\n            ) AS active_items\n        FROM field_missions\n        LEFT JOIN field_mission_items\n          ON field_mission_items.mission_id = field_missions.id\n        {where_clause}\n        GROUP BY field_missions.id\n        ORDER BY\n            field_missions.departure_date DESC,\n            field_missions.id DESC\n        LIMIT ? OFFSET ?\n        ",
        parameters,
    )


def mission_history_page_3(connection, parameters):
    return connection.execute(
        """
        SELECT DISTINCT destination
        FROM field_missions
        WHERE destination IS NOT NULL
          AND TRIM(destination) <> ''
        ORDER BY destination
    """,
        parameters,
    )


def mission_history_page_4(connection, parameters):
    return connection.execute(
        """
        SELECT DISTINCT team_name
        FROM field_missions
        WHERE team_name IS NOT NULL
          AND TRIM(team_name) <> ''
        ORDER BY team_name
    """,
        parameters,
    )


def mission_history_page_5(connection, parameters):
    return connection.execute(
        """
        SELECT DISTINCT substr(departure_date, 1, 4) AS year_value
        FROM field_missions
        WHERE departure_date IS NOT NULL
          AND length(departure_date) >= 4
        ORDER BY year_value DESC
    """,
        parameters,
    )


def individual_history_page_1(connection, parameters, where_clause):
    return connection.execute(f"SELECT COUNT(*) FROM loans {where_clause}", parameters)


def individual_history_page_2(connection, parameters, where_clause):
    return connection.execute(
        f"\n        SELECT\n            loans.*,\n            equipment.description,\n            equipment.manufacturer,\n            equipment.model,\n            equipment.serial_number,\n            equipment.dei_registry_number,\n            equipment.tem_internal_code,\n            equipment.location,\n            equipment.dexion,\n            equipment.shelf,\n            equipment.storage_column\n        FROM loans\n        JOIN equipment\n          ON equipment.id = loans.equipment_id\n        {where_clause}\n        ORDER BY\n            loans.checkout_date DESC,\n            loans.id DESC\n        LIMIT ? OFFSET ?\n        ",
        parameters,
    )


def individual_history_page_3(connection, parameters):
    return connection.execute(
        """
        SELECT DISTINCT substr(checkout_date, 1, 4) AS year_value
        FROM loans
        WHERE checkout_date IS NOT NULL
          AND length(checkout_date) >= 4
        ORDER BY year_value DESC
    """,
        parameters,
    )


MISSION_HISTORY_PAGE_SQL_1 = "field_missions.destination = ?"

MISSION_HISTORY_PAGE_SQL_2 = "field_missions.team_name = ?"

MISSION_HISTORY_PAGE_SQL_3 = "substr(field_missions.departure_date, 1, 4) = ?"

MISSION_HISTORY_PAGE_SQL_4 = "WHERE "

MISSION_HISTORY_PAGE_SQL_5 = " AND "

INDIVIDUAL_HISTORY_PAGE_SQL_6 = "WHERE substr(loans.checkout_date, 1, 4) = ?"
