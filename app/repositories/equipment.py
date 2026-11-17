"""Parameterized MySQL queries executed through SQLAlchemy Core."""


def equipment_list_1(connection, parameters, where_sql):
    return connection.execute("SELECT COUNT(*) FROM equipment" + where_sql, parameters)


def equipment_list_2(connection, parameters, where_sql):
    return connection.execute(
        "SELECT * FROM equipment" + where_sql + " ORDER BY id DESC LIMIT ? OFFSET ?", parameters
    )


def equipment_list_3(connection, parameters):
    return connection.execute(
        """
        SELECT DISTINCT category
        FROM equipment
        WHERE category IS NOT NULL
          AND TRIM(category) != ''
        ORDER BY category ASC
    """,
        parameters,
    )


def equipment_list_4(connection, parameters):
    return connection.execute(
        """
        SELECT DISTINCT manufacturer
        FROM equipment
        WHERE manufacturer IS NOT NULL
          AND TRIM(manufacturer) != ''
        ORDER BY manufacturer ASC
    """,
        parameters,
    )


def equipment_list_5(connection, parameters):
    return connection.execute(
        """
        SELECT DISTINCT status
        FROM equipment
        WHERE status IS NOT NULL
          AND TRIM(status) != ''
        ORDER BY status ASC
    """,
        parameters,
    )


def equipment_list_6(connection, parameters):
    return connection.execute(
        """
        SELECT DISTINCT location
        FROM equipment
        WHERE location IS NOT NULL
          AND TRIM(location) != ''
        ORDER BY location ASC
    """,
        parameters,
    )


def equipment_panel_data_1(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM equipment
        WHERE id = ?
    """,
        parameters,
    )


def equipment_panel_data_2(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM equipment_documents
        WHERE equipment_id = ?
        ORDER BY id DESC
    """,
        parameters,
    )


def equipment_panel_data_3(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM loans
        WHERE equipment_id = ?
        ORDER BY id DESC
        LIMIT 8
    """,
        parameters,
    )


def equipment_panel_data_4(connection, parameters):
    return connection.execute(
        """
        SELECT ea.id AS relation_id, e.*
        FROM equipment_alternatives ea
        JOIN equipment e ON e.id = ea.alternative_equipment_id
        WHERE ea.equipment_id = ?
        ORDER BY ea.priority ASC, ea.id ASC
    """,
        parameters,
    )


def upload_equipment_document_1(connection, parameters):
    return connection.execute(
        """
        SELECT id
        FROM equipment
        WHERE id = ?
    """,
        parameters,
    )


def upload_equipment_document_2(connection, parameters):
    return connection.execute(
        """
        INSERT INTO equipment_documents (
            equipment_id,
            original_name,
            stored_name,
            uploaded_at
        )
        VALUES (?, ?, ?, ?)
    """,
        parameters,
    )


def delete_equipment_document_1(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM equipment_documents
        WHERE id = ?
          AND equipment_id = ?
    """,
        parameters,
    )


def delete_equipment_document_2(connection, parameters):
    return connection.execute(
        """
        DELETE FROM equipment_documents
        WHERE id = ?
          AND equipment_id = ?
    """,
        parameters,
    )


def new_equipment_page_1(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM storage_locations
        WHERE active = 1
        ORDER BY dexion, shelf, storage_column
    """,
        parameters,
    )


def new_equipment_page_2(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM equipment_categories
        WHERE active = 1
        ORDER BY name ASC
    """,
        parameters,
    )


def create_equipment_1(connection, parameters):
    return connection.execute(
        """
        INSERT INTO equipment (

            code,
            description,
            category,
            manufacturer,
            model,
            serial_number,
            dei_registry_number,
            tem_internal_code,
            dexion,
            shelf,
            storage_column,
            location,
            status,
            quantity,
            notes,
            equipment_photo,
            location_photo

        )

        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """,
        parameters,
    )


def checkout_equipment_1(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM equipment
        WHERE id = ?
    """,
        parameters,
    )


def checkout_equipment_2(connection, parameters):
    return connection.execute(
        """
        INSERT INTO loans (

            equipment_id,
            borrower_name,
            borrower_unit,
            checkout_date,
            expected_return_date,
            checkout_notes,
            active,
            created_at

        )

        VALUES (?, ?, ?, ?, ?, ?, 1, ?)
    """,
        parameters,
    )


def checkout_equipment_3(connection, parameters):
    return connection.execute(
        """
        UPDATE equipment
        SET status = 'Σε Χρήση'
        WHERE id = ?
    """,
        parameters,
    )


def delete_equipment_1(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM equipment
        WHERE id = ?
    """,
        parameters,
    )


def delete_equipment_2(connection, parameters):
    return connection.execute(
        """
        SELECT stored_name
        FROM equipment_documents
        WHERE equipment_id = ?
    """,
        parameters,
    )


def delete_equipment_3(connection, parameters):
    return connection.execute(
        """
        DELETE FROM equipment_documents
        WHERE equipment_id = ?
    """,
        parameters,
    )


def delete_equipment_4(connection, parameters):
    return connection.execute(
        """
        DELETE FROM loans
        WHERE equipment_id = ?
    """,
        parameters,
    )


def delete_equipment_5(connection, parameters):
    return connection.execute(
        """
        DELETE FROM equipment
        WHERE id = ?
    """,
        parameters,
    )


def add_equipment_alternative_1(connection, parameters):
    return connection.execute("SELECT id FROM equipment WHERE id = ?", parameters)


def add_equipment_alternative_2(connection, parameters):
    return connection.execute(
        """
        SELECT * FROM equipment
        WHERE lower(trim(code)) = lower(?)
           OR lower(trim(COALESCE(dei_registry_number,''))) = lower(?)
           OR lower(trim(COALESCE(tem_internal_code,''))) = lower(?)
        ORDER BY id ASC LIMIT 1
    """,
        parameters,
    )


def add_equipment_alternative_3(connection, parameters):
    return connection.execute(
        """
        SELECT 1 FROM equipment_alternatives
        WHERE equipment_id = ? AND alternative_equipment_id = ?
    """,
        parameters,
    )


def add_equipment_alternative_4(connection, parameters):
    return connection.execute(
        "SELECT COALESCE(MAX(priority),0)+1 FROM equipment_alternatives WHERE equipment_id = ?",
        parameters,
    )


def add_equipment_alternative_5(connection, parameters):
    return connection.execute(
        """
            INSERT INTO equipment_alternatives(equipment_id, alternative_equipment_id, priority, created_at)
            VALUES (?, ?, ?, ?)
        """,
        parameters,
    )


def delete_equipment_alternative_1(connection, parameters):
    return connection.execute(
        "DELETE FROM equipment_alternatives WHERE id = ? AND equipment_id = ?", parameters
    )


def equipment_detail_1(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM equipment
        WHERE id = ?
    """,
        parameters,
    )


def equipment_detail_2(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM equipment_documents
        WHERE equipment_id = ?
        ORDER BY id DESC
    """,
        parameters,
    )


def equipment_detail_3(connection, parameters):
    return connection.execute(
        """
        SELECT ea.id AS relation_id, ea.priority, e.*
        FROM equipment_alternatives ea
        JOIN equipment e ON e.id = ea.alternative_equipment_id
        WHERE ea.equipment_id = ?
        ORDER BY ea.priority ASC, ea.id ASC
    """,
        parameters,
    )


def equipment_detail_4(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM loans
        WHERE equipment_id = ?
        ORDER BY
            checkout_date DESC,
            id DESC
    """,
        parameters,
    )


def equipment_edit_page_1(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM equipment
        WHERE id = ?
    """,
        parameters,
    )


def equipment_edit_page_2(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM storage_locations
        WHERE active = 1
        ORDER BY
            dexion,
            shelf,
            storage_column
    """,
        parameters,
    )


def equipment_edit_page_3(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM equipment_categories
        WHERE active = 1
        ORDER BY name ASC
    """,
        parameters,
    )


def equipment_edit_page_4(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM equipment_documents
        WHERE equipment_id = ?
        ORDER BY id DESC
    """,
        parameters,
    )


def update_equipment_1(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM equipment
        WHERE id = ?
    """,
        parameters,
    )


def update_equipment_2(connection, parameters):
    return connection.execute(
        """
        UPDATE equipment

        SET
            code = ?,
            description = ?,
            category = ?,
            manufacturer = ?,
            model = ?,
            serial_number = ?,
            dei_registry_number = ?,
            tem_internal_code = ?,
            dexion = ?,
            shelf = ?,
            storage_column = ?,
            location = ?,
            status = ?,
            quantity = ?,
            notes = ?,
            equipment_photo = ?,
            location_photo = ?

        WHERE id = ?
    """,
        parameters,
    )


EQUIPMENT_LIST_SQL_1 = """
            (
                description LIKE ?
                OR category LIKE ?
                OR manufacturer LIKE ?
                OR model LIKE ?
                OR serial_number LIKE ?
                OR location LIKE ?
                OR dei_registry_number LIKE ?
                OR tem_internal_code LIKE ?
                OR code LIKE ?
                OR dexion LIKE ?
                OR shelf LIKE ?
                OR storage_column LIKE ?
            )
        """

EQUIPMENT_LIST_SQL_2 = "category = ?"

EQUIPMENT_LIST_SQL_3 = "manufacturer = ?"

EQUIPMENT_LIST_SQL_4 = "status = ?"

EQUIPMENT_LIST_SQL_5 = "location = ?"

EQUIPMENT_LIST_SQL_6 = " WHERE "

EQUIPMENT_LIST_SQL_7 = " AND "
