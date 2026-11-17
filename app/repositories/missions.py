"""Parameterized MySQL queries executed through SQLAlchemy Core."""


def checkout_return_page_1(connection, parameters):
    return connection.execute(
        """
            SELECT *
            FROM equipment

            WHERE status = 'Διαθέσιμο'

            AND (
                description LIKE ?
                OR manufacturer LIKE ?
                OR model LIKE ?
                OR serial_number LIKE ?
                OR dei_registry_number LIKE ?
                OR tem_internal_code LIKE ?
                OR location LIKE ?
                OR code LIKE ?
                OR dexion LIKE ?
                OR shelf LIKE ?
                OR storage_column LIKE ?
            )

            ORDER BY description ASC
        """,
        parameters,
    )


def checkout_return_page_2(connection, parameters):
    return connection.execute(
        """
        SELECT

            loans.*,

            equipment.description,
            equipment.manufacturer,
            equipment.model,
            equipment.serial_number,
            equipment.dei_registry_number,
            equipment.tem_internal_code,
            equipment.location,
            equipment.dexion,
            equipment.shelf,
            equipment.storage_column

        FROM loans

        JOIN equipment
          ON equipment.id = loans.equipment_id

        WHERE loans.active = 1

        ORDER BY
            loans.checkout_date DESC,
            loans.id DESC
    """,
        parameters,
    )


def checkout_return_page_3(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM measurement_teams
        WHERE active = 1
        ORDER BY name ASC
    """,
        parameters,
    )


def checkout_return_page_4(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM app_settings
        WHERE id = 1
    """,
        parameters,
    )


def checkout_return_page_5(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM mission_vehicles
        WHERE active = 1
        ORDER BY model ASC, license_plate ASC
    """,
        parameters,
    )


def checkout_return_page_6(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM mission_destinations
        WHERE active = 1
        ORDER BY name ASC
    """,
        parameters,
    )


def checkout_return_page_7(connection, parameters):
    return connection.execute(
        """
        SELECT

            field_missions.*,

            COUNT(field_mission_items.id)
                AS total_items,

            SUM(
                CASE
                    WHEN field_mission_items.status = 'Επιστράφηκε'
                    THEN 1
                    ELSE 0
                END
            ) AS returned_items

        FROM field_missions

        LEFT JOIN field_mission_items
          ON field_mission_items.mission_id = field_missions.id

        WHERE field_missions.status IN ('Προετοιμασία', 'Ενεργή')

        GROUP BY field_missions.id

        ORDER BY
            CASE field_missions.status
                WHEN 'Ενεργή' THEN 1
                WHEN 'Προετοιμασία' THEN 2
                ELSE 3
            END,
            field_missions.departure_date DESC,
            field_missions.id DESC
    """,
        parameters,
    )


def checkout_return_page_8(connection, parameters):
    return connection.execute(
        """
            SELECT *
            FROM field_missions
            WHERE id = ?
        """,
        parameters,
    )


def checkout_return_page_9(connection, parameters):
    return connection.execute(
        """
                SELECT

                    field_mission_items.*,

                    equipment.description,
                    equipment.manufacturer,
                    equipment.model,
                    equipment.serial_number,
                    equipment.dei_registry_number,
                    equipment.tem_internal_code,
                    equipment.equipment_photo,
                    equipment.location,
                    equipment.dexion,
                    equipment.shelf,
                    equipment.storage_column

                FROM field_mission_items

                JOIN equipment
                  ON equipment.id = field_mission_items.equipment_id

                WHERE field_mission_items.mission_id = ?

                ORDER BY field_mission_items.id ASC
            """,
        parameters,
    )


def checkout_return_page_10(connection, parameters):
    return connection.execute(
        """
                    SELECT *
                    FROM equipment

                    WHERE status = 'Διαθέσιμο'

                      AND id NOT IN (
                          SELECT equipment_id
                          FROM field_mission_items
                          WHERE mission_id = ?
                      )

                      AND (
                          description LIKE ?
                          OR manufacturer LIKE ?
                          OR model LIKE ?
                          OR serial_number LIKE ?
                          OR dei_registry_number LIKE ?
                          OR tem_internal_code LIKE ?
                          OR location LIKE ?
                          OR code LIKE ?
                          OR dexion LIKE ?
                          OR shelf LIKE ?
                          OR storage_column LIKE ?
                      )

                    ORDER BY description ASC
                """,
        parameters,
    )


def checkout_return_page_11(connection, parameters):
    return connection.execute(
        """
        SELECT pl.*, COUNT(pli.id) AS item_count
        FROM picking_lists pl
        LEFT JOIN picking_list_items pli ON pli.picking_list_id = pl.id
        WHERE pl.status IN ('Draft', 'Έτοιμη')
        GROUP BY pl.id
        ORDER BY COALESCE(pl.travel_date, '9999-12-31') ASC, pl.id DESC
    """,
        parameters,
    )


def checkout_return_page_12(connection, parameters):
    return connection.execute("SELECT * FROM picking_lists WHERE id = ?", parameters)


def checkout_return_page_13(connection, parameters):
    return connection.execute(
        """
                SELECT pli.id AS picking_item_id, e.*,
                       (SELECT ea.alternative_equipment_id
                        FROM equipment_alternatives ea
                        JOIN equipment ae ON ae.id = ea.alternative_equipment_id
                        WHERE ea.equipment_id = e.id
                          AND ae.status = 'Διαθέσιμο'
                        ORDER BY ea.priority ASC, ea.id ASC LIMIT 1) AS available_alternative_id,
                       (SELECT ae.code
                        FROM equipment_alternatives ea
                        JOIN equipment ae ON ae.id = ea.alternative_equipment_id
                        WHERE ea.equipment_id = e.id
                          AND ae.status = 'Διαθέσιμο'
                        ORDER BY ea.priority ASC, ea.id ASC LIMIT 1) AS available_alternative_code,
                       (SELECT ae.description
                        FROM equipment_alternatives ea
                        JOIN equipment ae ON ae.id = ea.alternative_equipment_id
                        WHERE ea.equipment_id = e.id
                          AND ae.status = 'Διαθέσιμο'
                        ORDER BY ea.priority ASC, ea.id ASC LIMIT 1) AS available_alternative_description
                FROM picking_list_items pli
                JOIN equipment e ON e.id = pli.equipment_id
                WHERE pli.picking_list_id = ?
                ORDER BY pli.id ASC
            """,
        parameters,
    )


def return_equipment_1(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM loans

        WHERE id = ?
          AND active = 1
    """,
        parameters,
    )


def return_equipment_2(connection, parameters):
    return connection.execute(
        """
        UPDATE loans

        SET
            return_date = ?,
            return_notes = ?,
            active = 0

        WHERE id = ?
    """,
        parameters,
    )


def return_equipment_3(connection, parameters):
    return connection.execute(
        """
        UPDATE equipment
        SET status = 'Διαθέσιμο'
        WHERE id = ?
    """,
        parameters,
    )


def mission_detail_page_1(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM field_missions
        WHERE id = ?
    """,
        parameters,
    )


def mission_detail_page_2(connection, parameters):
    return connection.execute(
        """
        SELECT

            field_mission_items.*,

            equipment.description,
            equipment.manufacturer,
            equipment.model,
            equipment.serial_number,
            equipment.dei_registry_number,
            equipment.tem_internal_code,
            equipment.equipment_photo,
            equipment.location,
            equipment.dexion,
            equipment.shelf,
            equipment.storage_column

        FROM field_mission_items

        JOIN equipment
          ON equipment.id = field_mission_items.equipment_id

        WHERE field_mission_items.mission_id = ?

        ORDER BY field_mission_items.id ASC
    """,
        parameters,
    )


def mission_detail_page_3(connection, parameters):
    return connection.execute(
        """
            SELECT *
            FROM equipment

            WHERE status = 'Διαθέσιμο'

              AND id NOT IN (
                  SELECT equipment_id
                  FROM field_mission_items
                  WHERE mission_id = ?
              )

              AND (
                  description LIKE ?
                  OR manufacturer LIKE ?
                  OR model LIKE ?
                  OR serial_number LIKE ?
                  OR dei_registry_number LIKE ?
                  OR tem_internal_code LIKE ?
                  OR location LIKE ?
                  OR code LIKE ?
                  OR dexion LIKE ?
                  OR shelf LIKE ?
                  OR storage_column LIKE ?
              )

            ORDER BY description ASC
        """,
        parameters,
    )


def mission_detail_page_4(connection, parameters):
    return connection.execute(
        """
        SELECT pl.*, COUNT(pli.id) AS item_count
        FROM picking_lists pl
        LEFT JOIN picking_list_items pli ON pli.picking_list_id = pl.id
        GROUP BY pl.id
        ORDER BY pl.updated_at DESC, pl.id DESC
    """,
        parameters,
    )


def mission_detail_page_5(connection, parameters):
    return connection.execute("SELECT * FROM picking_lists WHERE id = ?", parameters)


def mission_detail_page_6(connection, parameters):
    return connection.execute(
        """
                SELECT
                    pli.id AS picking_item_id,
                    e.*,
                    (
                        SELECT ea.alternative_equipment_id
                        FROM equipment_alternatives ea
                        JOIN equipment ae
                          ON ae.id = ea.alternative_equipment_id
                        WHERE ea.equipment_id = e.id
                          AND ae.status = 'Διαθέσιμο'
                        ORDER BY ea.priority ASC, ea.id ASC
                        LIMIT 1
                    ) AS available_alternative_id,
                    (
                        SELECT ae.code
                        FROM equipment_alternatives ea
                        JOIN equipment ae
                          ON ae.id = ea.alternative_equipment_id
                        WHERE ea.equipment_id = e.id
                          AND ae.status = 'Διαθέσιμο'
                        ORDER BY ea.priority ASC, ea.id ASC
                        LIMIT 1
                    ) AS available_alternative_code,
                    (
                        SELECT ae.description
                        FROM equipment_alternatives ea
                        JOIN equipment ae
                          ON ae.id = ea.alternative_equipment_id
                        WHERE ea.equipment_id = e.id
                          AND ae.status = 'Διαθέσιμο'
                        ORDER BY ea.priority ASC, ea.id ASC
                        LIMIT 1
                    ) AS available_alternative_description
                FROM picking_list_items pli
                JOIN equipment e ON e.id = pli.equipment_id
                WHERE pli.picking_list_id = ?
                ORDER BY pli.id ASC
            """,
        parameters,
    )


def delete_field_mission_1(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM field_missions
        WHERE id = ?
    """,
        parameters,
    )


def delete_field_mission_2(connection, parameters):
    return connection.execute(
        """
        SELECT
            field_mission_items.equipment_id,
            field_mission_items.status
        FROM field_mission_items
        WHERE mission_id = ?
    """,
        parameters,
    )


def delete_field_mission_3(connection, parameters):
    return connection.execute(
        """
                UPDATE equipment
                SET status = 'Διαθέσιμο'
                WHERE id = ?
                  AND status = 'Σε Αποστολή'
            """,
        parameters,
    )


def delete_field_mission_4(connection, parameters):
    return connection.execute(
        """
        DELETE FROM field_mission_items
        WHERE mission_id = ?
    """,
        parameters,
    )


def delete_field_mission_5(connection, parameters):
    return connection.execute(
        """
        DELETE FROM field_missions
        WHERE id = ?
    """,
        parameters,
    )


def create_field_mission_1(connection, parameters):
    return connection.execute(
        """
        INSERT INTO field_missions (

            destination,
            team_name,
            departure_date,
            expected_return_date,
            vehicle,
            license_plate,
            notes,
            status,
            created_at

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, 'Προετοιμασία', ?)
    """,
        parameters,
    )


def create_field_mission_2(connection, parameters):
    return connection.execute(
        """
        UPDATE field_missions
        SET mission_code = ?
        WHERE id = ?
    """,
        parameters,
    )


def mission_replace_picking_item_1(connection, parameters):
    return connection.execute("SELECT * FROM field_missions WHERE id = ?", parameters)


def mission_replace_picking_item_2(connection, parameters):
    return connection.execute("SELECT * FROM equipment WHERE id = ?", parameters)


def mission_replace_picking_item_3(connection, parameters):
    return connection.execute(
        """
            UPDATE picking_list_items
            SET equipment_id = ?
            WHERE id = ?
              AND picking_list_id = ?
        """,
        parameters,
    )


def load_picking_list_into_mission_1(connection, parameters):
    return connection.execute("SELECT * FROM field_missions WHERE id = ?", parameters)


def load_picking_list_into_mission_2(connection, parameters):
    return connection.execute("SELECT * FROM picking_lists WHERE id = ?", parameters)


def load_picking_list_into_mission_3(connection, parameters):
    return connection.execute(
        """
        SELECT e.*
        FROM picking_list_items pli
        JOIN equipment e ON e.id = pli.equipment_id
        WHERE pli.picking_list_id = ?
        ORDER BY pli.id ASC
    """,
        parameters,
    )


def load_picking_list_into_mission_4(connection, parameters):
    return connection.execute(
        """
            SELECT id
            FROM field_mission_items
            WHERE mission_id = ?
              AND equipment_id = ?
        """,
        parameters,
    )


def load_picking_list_into_mission_5(connection, parameters):
    return connection.execute(
        """
            INSERT INTO field_mission_items (
                mission_id,
                equipment_id,
                status,
                added_at
            )
            VALUES (?, ?, ?, ?)
        """,
        parameters,
    )


def load_picking_list_into_mission_6(connection, parameters):
    return connection.execute(
        """
                UPDATE equipment
                SET status = 'Σε Αποστολή'
                WHERE id = ?
                  AND status = 'Διαθέσιμο'
            """,
        parameters,
    )


def load_picking_list_into_mission_7(connection, parameters):
    return connection.execute(
        """
        UPDATE picking_lists
        SET status = 'Χρησιμοποιήθηκε',
            updated_at = ?
        WHERE id = ?
    """,
        parameters,
    )


def add_mission_items_bulk_1(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM field_missions
        WHERE id = ?
    """,
        parameters,
    )


def add_mission_items_bulk_2(connection, parameters):
    return connection.execute(
        """
            SELECT *
            FROM equipment
            WHERE id = ?
        """,
        parameters,
    )


def add_mission_items_bulk_3(connection, parameters):
    return connection.execute(
        """
            SELECT id
            FROM field_mission_items
            WHERE mission_id = ?
              AND equipment_id = ?
        """,
        parameters,
    )


def add_mission_items_bulk_4(connection, parameters):
    return connection.execute(
        """
            INSERT INTO field_mission_items (
                mission_id,
                equipment_id,
                status,
                added_at
            )
            VALUES (?, ?, ?, ?)
        """,
        parameters,
    )


def add_mission_items_bulk_5(connection, parameters):
    return connection.execute(
        """
                UPDATE equipment
                SET status = 'Σε Αποστολή'
                WHERE id = ?
            """,
        parameters,
    )


def add_equipment_to_mission_1(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM field_missions
        WHERE id = ?
    """,
        parameters,
    )


def add_equipment_to_mission_2(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM equipment
        WHERE id = ?
    """,
        parameters,
    )


def add_equipment_to_mission_3(connection, parameters):
    return connection.execute(
        """
            INSERT INTO field_mission_items (

                mission_id,
                equipment_id,
                status,
                added_at

            )

            VALUES (?, ?, ?, ?)
        """,
        parameters,
    )


def add_equipment_to_mission_4(connection, parameters):
    return connection.execute(
        """
                UPDATE equipment
                SET status = 'Σε Αποστολή'
                WHERE id = ?
            """,
        parameters,
    )


def remove_equipment_from_mission_draft_1(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM field_missions
        WHERE id = ?
    """,
        parameters,
    )


def remove_equipment_from_mission_draft_2(connection, parameters):
    return connection.execute(
        """
        DELETE FROM field_mission_items

        WHERE id = ?
          AND mission_id = ?
    """,
        parameters,
    )


def start_field_mission_1(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM field_missions
        WHERE id = ?
    """,
        parameters,
    )


def start_field_mission_2(connection, parameters):
    return connection.execute(
        """
        SELECT

            field_mission_items.id,
            field_mission_items.equipment_id,
            equipment.status AS equipment_status,
            equipment.description

        FROM field_mission_items

        JOIN equipment
          ON equipment.id = field_mission_items.equipment_id

        WHERE field_mission_items.mission_id = ?
    """,
        parameters,
    )


def start_field_mission_3(connection, parameters, placeholders):
    return connection.execute(
        f"\n        UPDATE equipment\n        SET status = 'Σε Αποστολή'\n        WHERE id IN ({placeholders})\n        ",
        parameters,
    )


def start_field_mission_4(connection, parameters):
    return connection.execute(
        """
        UPDATE field_mission_items
        SET status = 'Σε Αποστολή'
        WHERE mission_id = ?
    """,
        parameters,
    )


def start_field_mission_5(connection, parameters):
    return connection.execute(
        """
        UPDATE field_missions
        SET status = 'Ενεργή'
        WHERE id = ?
    """,
        parameters,
    )


def return_mission_item_1(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM field_mission_items

        WHERE id = ?
          AND mission_id = ?
          AND status = 'Σε Αποστολή'
    """,
        parameters,
    )


def return_mission_item_2(connection, parameters):
    return connection.execute(
        """
        UPDATE field_mission_items

        SET
            status = 'Επιστράφηκε',
            returned_at = ?,
            return_notes = ?

        WHERE id = ?
    """,
        parameters,
    )


def return_mission_item_3(connection, parameters):
    return connection.execute(
        """
        UPDATE equipment
        SET status = 'Διαθέσιμο'
        WHERE id = ?
    """,
        parameters,
    )


def return_mission_item_4(connection, parameters):
    return connection.execute(
        """
        SELECT COUNT(*)
        FROM field_mission_items

        WHERE mission_id = ?
          AND status = 'Σε Αποστολή'
          AND id != ?
    """,
        parameters,
    )


def return_mission_item_5(connection, parameters):
    return connection.execute(
        """
            UPDATE field_missions

            SET
                status = 'Ολοκληρωμένη',
                completed_at = ?

            WHERE id = ?
        """,
        parameters,
    )


def return_all_mission_items_1(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM field_mission_items

        WHERE mission_id = ?
          AND status = 'Σε Αποστολή'
    """,
        parameters,
    )


def return_all_mission_items_2(connection, parameters):
    return connection.execute(
        """
        UPDATE field_mission_items

        SET
            status = 'Επιστράφηκε',
            returned_at = ?,
            return_notes = ?

        WHERE mission_id = ?
          AND status = 'Σε Αποστολή'
    """,
        parameters,
    )


def return_all_mission_items_3(connection, parameters, placeholders):
    return connection.execute(
        f"\n        UPDATE equipment\n        SET status = 'Διαθέσιμο'\n        WHERE id IN ({placeholders})\n        ",
        parameters,
    )


def return_all_mission_items_4(connection, parameters):
    return connection.execute(
        """
        UPDATE field_missions

        SET
            status = 'Ολοκληρωμένη',
            completed_at = ?

        WHERE id = ?
    """,
        parameters,
    )


def delete_history_movement_1(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM loans
        WHERE id = ?
    """,
        parameters,
    )


def delete_history_movement_2(connection, parameters):
    return connection.execute(
        """
        DELETE FROM loans
        WHERE id = ?
    """,
        parameters,
    )


def delete_history_movement_3(connection, parameters):
    return connection.execute(
        """
        SELECT COUNT(*)
        FROM loans
        WHERE equipment_id = ?
          AND active = 1
    """,
        parameters,
    )


def delete_history_movement_4(connection, parameters):
    return connection.execute(
        """
            UPDATE equipment
            SET status = 'Διαθέσιμο'
            WHERE id = ?
              AND status = 'Σε Χρήση'
        """,
        parameters,
    )
