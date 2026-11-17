"""Parameterized MySQL queries executed through SQLAlchemy Core."""


def categories_page_1(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM equipment_categories
        ORDER BY name ASC
    """,
        parameters,
    )


def create_category_1(connection, parameters):
    return connection.execute(
        """
        SELECT id
        FROM equipment_categories
        WHERE LOWER(name) = LOWER(?)
    """,
        parameters,
    )


def create_category_2(connection, parameters):
    return connection.execute(
        """
        INSERT INTO equipment_categories (
            name,
            description,
            active
        )
        VALUES (?, ?, 1)
    """,
        parameters,
    )


def edit_category_1(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM equipment_categories
        WHERE id = ?
    """,
        parameters,
    )


def edit_category_2(connection, parameters):
    return connection.execute(
        """
        SELECT id
        FROM equipment_categories
        WHERE LOWER(name) = LOWER(?)
          AND id != ?
    """,
        parameters,
    )


def edit_category_3(connection, parameters):
    return connection.execute(
        """
        UPDATE equipment_categories
        SET
            name = ?,
            description = ?
        WHERE id = ?
    """,
        parameters,
    )


def edit_category_4(connection, parameters):
    return connection.execute(
        """
            UPDATE equipment
            SET category = ?
            WHERE category = ?
        """,
        parameters,
    )


def delete_category_1(connection, parameters):
    return connection.execute(
        """
        SELECT *
        FROM equipment_categories
        WHERE id = ?
    """,
        parameters,
    )


def delete_category_2(connection, parameters):
    return connection.execute(
        """
        SELECT COUNT(*)
        FROM equipment
        WHERE category = ?
    """,
        parameters,
    )


def delete_category_3(connection, parameters):
    return connection.execute(
        """
        DELETE FROM equipment_categories
        WHERE id = ?
    """,
        parameters,
    )
