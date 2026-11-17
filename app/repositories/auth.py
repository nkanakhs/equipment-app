"""Parameterized MySQL queries executed through SQLAlchemy Core."""


def login_1(connection, parameters):
    return connection.execute(
        "SELECT * FROM users WHERE LOWER(username) = LOWER(?) LIMIT 1", parameters
    )


def login_2(connection, parameters):
    return connection.execute("UPDATE users SET last_login = ? WHERE id = ?", parameters)


def account_change_password_1(connection, parameters):
    return connection.execute("UPDATE users SET password_hash = ? WHERE id = ?", parameters)


def account_change_password_2(connection, parameters):
    return connection.execute("DELETE FROM user_sessions WHERE user_id = ?", parameters)


def admin_create_user_1(connection, parameters):
    return connection.execute(
        """
                INSERT INTO users(
                    username, password_hash, full_name,
                    role, active, created_at
                )
                VALUES (?, ?, ?, ?, 1, ?)
            """,
        parameters,
    )


def admin_update_user_1(connection, parameters):
    return connection.execute("SELECT * FROM users WHERE id = ?", parameters)


def admin_update_user_2(connection, parameters):
    return connection.execute(
        """
            SELECT id
            FROM users
            WHERE id <> ?
              AND LOWER(username) = LOWER(?)
            LIMIT 1
        """,
        parameters,
    )


def admin_update_user_3(connection, parameters):
    return connection.execute(
        """
            UPDATE users
            SET full_name = ?, username = ?, role = ?, active = ?
            WHERE id = ?
        """,
        parameters,
    )


def admin_update_user_4(connection, parameters):
    return connection.execute("DELETE FROM user_sessions WHERE user_id = ?", parameters)


def admin_reset_user_password_1(connection, parameters):
    return connection.execute("UPDATE users SET password_hash = ? WHERE id = ?", parameters)


def admin_reset_user_password_2(connection, parameters):
    return connection.execute("DELETE FROM user_sessions WHERE user_id = ?", parameters)
