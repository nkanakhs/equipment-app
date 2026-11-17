"""Parameterized MySQL queries executed through SQLAlchemy Core."""


def home_1(connection, parameters):
    return connection.execute(
        """
        SELECT COUNT(*)
        FROM equipment
    """,
        parameters,
    )


def home_2(connection, parameters):
    return connection.execute(
        """
        SELECT COUNT(*)
        FROM equipment
        WHERE status = 'Διαθέσιμο'
    """,
        parameters,
    )


def home_3(connection, parameters):
    return connection.execute(
        """
        SELECT COUNT(*)
        FROM equipment
        WHERE status = 'Σε Χρήση'
    """,
        parameters,
    )


def home_4(connection, parameters):
    return connection.execute(
        """
        SELECT COUNT(*)
        FROM equipment
        WHERE status = 'Σε Αποστολή'
    """,
        parameters,
    )


def home_5(connection, parameters):
    return connection.execute(
        """
        SELECT COUNT(*)
        FROM equipment
        WHERE status = 'Σε Συντήρηση'
    """,
        parameters,
    )


def home_6(connection, parameters):
    return connection.execute(
        """
        SELECT COUNT(*)
        FROM equipment
        WHERE status = 'Εκτός Λειτουργίας'
    """,
        parameters,
    )


def home_7(connection, parameters):
    return connection.execute(
        """
        SELECT COUNT(*)
        FROM loans
        WHERE active = 1
    """,
        parameters,
    )


def home_8(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM (

            SELECT
                loans.id AS loan_id,
                equipment.id AS equipment_id,
                equipment.description,
                equipment.manufacturer,
                equipment.model,
                equipment.code,
                loans.borrower_name,
                loans.checkout_date AS movement_date,
                'Χρέωση' AS movement_type

            FROM loans

            JOIN equipment
              ON equipment.id = loans.equipment_id

            UNION ALL

            SELECT
                loans.id AS loan_id,
                equipment.id AS equipment_id,
                equipment.description,
                equipment.manufacturer,
                equipment.model,
                equipment.code,
                loans.borrower_name,
                loans.return_date AS movement_date,
                'Επιστροφή' AS movement_type

            FROM loans

            JOIN equipment
              ON equipment.id = loans.equipment_id

            WHERE loans.return_date IS NOT NULL
              AND TRIM(loans.return_date) <> ''

        ) AS recent_movements

        ORDER BY movement_date DESC, loan_id DESC

        LIMIT 5
    """,
        parameters,
    )


def home_9(connection, parameters):
    return connection.execute(
        """
        SELECT

            status,

            COUNT(*) AS count

        FROM equipment

        GROUP BY status

        ORDER BY count DESC
    """,
        parameters,
    )


def home_10(connection, parameters):
    return connection.execute(
        """
        SELECT

            CASE
                WHEN category IS NULL
                     OR TRIM(category) = ''
                THEN 'Χωρίς Κατηγορία'
                ELSE category
            END AS category,

            COUNT(*) AS count

        FROM equipment

        GROUP BY category

        ORDER BY count DESC, category ASC

        LIMIT 8
    """,
        parameters,
    )


def home_11(connection, parameters):
    return connection.execute(
        """
        SELECT id, station_code, name, category, energy_source,
               area_system, address, latitude, longitude,
               coordinate_accuracy, operational_status,
               notes, is_location_verified, show_on_map, active
        FROM mission_destinations
        WHERE latitude IS NOT NULL
          AND longitude IS NOT NULL
          AND COALESCE(show_on_map, 1) = 1
        ORDER BY name ASC
    """,
        parameters,
    )


def home_12(connection, parameters):
    return connection.execute(
        """
        SELECT
            fm.id,
            fm.mission_code,
            fm.destination,
            fm.team_name,
            fm.departure_date,
            fm.vehicle,
            fm.license_plate,
            md.latitude,
            md.longitude,
            (
                SELECT COUNT(*)
                FROM field_mission_items fmi
                WHERE fmi.mission_id = fm.id
                  AND fmi.returned_at IS NULL
            ) AS equipment_count
        FROM field_missions fm
        LEFT JOIN mission_destinations md
          ON LOWER(TRIM(md.name)) = LOWER(TRIM(fm.destination))
        WHERE fm.status = 'Ενεργή'
        ORDER BY fm.departure_date DESC, fm.id DESC
    """,
        parameters,
    )


def home_13(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM app_settings
        WHERE id = 1
    """,
        parameters,
    )
