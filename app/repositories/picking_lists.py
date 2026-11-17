"""Parameterized MySQL queries executed through SQLAlchemy Core."""


def picking_lists_page_1(connection, parameters):
    return connection.execute(
        """
        SELECT pl.*, COUNT(pli.id) AS item_count
        FROM picking_lists pl
        LEFT JOIN picking_list_items pli ON pli.picking_list_id = pl.id
        GROUP BY pl.id
        ORDER BY pl.id DESC
    """,
        parameters,
    )


def picking_lists_page_2(connection, parameters):
    return connection.execute("SELECT * FROM picking_lists WHERE id = ?", parameters)


def picking_lists_page_3(connection, parameters):
    return connection.execute(
        """
                SELECT pli.id AS picking_item_id, e.*
                FROM picking_list_items pli
                JOIN equipment e ON e.id = pli.equipment_id
                WHERE pli.picking_list_id = ?
                ORDER BY pli.id ASC
            """,
        parameters,
    )


def picking_lists_page_4(connection, parameters):
    return connection.execute(
        """
                    SELECT * FROM equipment
                    WHERE id NOT IN (SELECT equipment_id FROM picking_list_items WHERE picking_list_id = ?)
                      AND (description LIKE ? OR manufacturer LIKE ? OR model LIKE ? OR serial_number LIKE ?
                           OR dei_registry_number LIKE ? OR tem_internal_code LIKE ? OR code LIKE ? OR location LIKE ?)
                    ORDER BY description ASC LIMIT 40
                """,
        parameters,
    )


def create_picking_list_1(connection, parameters):
    return connection.execute(
        """
        INSERT INTO picking_lists(title,destination,travel_date,team_name,notes,status,created_at,updated_at)
        VALUES (?,?,?,?,?,'Draft',?,?)
    """,
        parameters,
    )


def create_picking_list_2(connection, parameters):
    return connection.execute("UPDATE picking_lists SET list_code = ? WHERE id = ?", parameters)


def update_picking_list_1(connection, parameters):
    return connection.execute(
        "UPDATE picking_lists SET title=?,destination=?,travel_date=?,team_name=?,notes=?,status=?,updated_at=? WHERE id=?",
        parameters,
    )


def api_add_picking_item_1(connection, parameters):
    return connection.execute("SELECT * FROM picking_lists WHERE id=?", parameters)


def api_add_picking_item_2(connection, parameters):
    return connection.execute("SELECT * FROM equipment WHERE id=?", parameters)


def api_add_picking_item_3(connection, parameters):
    return connection.execute(
        """
        SELECT e.* FROM equipment_alternatives ea
        JOIN equipment e ON e.id=ea.alternative_equipment_id
        WHERE ea.equipment_id=? AND e.status='Διαθέσιμο'
        ORDER BY ea.priority ASC, ea.id ASC LIMIT 1
    """,
        parameters,
    )


def api_add_picking_item_4(connection, parameters):
    return connection.execute(
        "INSERT INTO picking_list_items(picking_list_id,equipment_id,created_at) VALUES(?,?,?)",
        parameters,
    )


def api_add_picking_item_5(connection, parameters):
    return connection.execute("UPDATE picking_lists SET updated_at=? WHERE id=?", parameters)


def delete_picking_item_1(connection, parameters):
    return connection.execute(
        "DELETE FROM picking_list_items WHERE id=? AND picking_list_id=?", parameters
    )


def replace_picking_item_1(connection, parameters):
    return connection.execute("SELECT * FROM equipment WHERE id=?", parameters)


def replace_picking_item_2(connection, parameters):
    return connection.execute(
        "UPDATE picking_list_items SET equipment_id=? WHERE id=? AND picking_list_id=?", parameters
    )


def checkout_picking_list_1(connection, parameters):
    return connection.execute("SELECT * FROM picking_lists WHERE id=?", parameters)


def checkout_picking_list_2(connection, parameters):
    return connection.execute(
        "SELECT e.* FROM picking_list_items pli JOIN equipment e ON e.id=pli.equipment_id WHERE pli.picking_list_id=? ORDER BY pli.id",
        parameters,
    )


def checkout_picking_list_3(connection, parameters):
    return connection.execute(
        "INSERT INTO loans(equipment_id,borrower_name,borrower_unit,checkout_date,expected_return_date,checkout_notes,active,created_at) VALUES(?,?,?,?,?,?,1,?)",
        parameters,
    )


def checkout_picking_list_4(connection, parameters):
    return connection.execute("UPDATE equipment SET status='Σε Χρήση' WHERE id=?", parameters)


def checkout_picking_list_5(connection, parameters):
    return connection.execute(
        "UPDATE picking_lists SET status='Χρησιμοποιήθηκε',updated_at=? WHERE id=?", parameters
    )
