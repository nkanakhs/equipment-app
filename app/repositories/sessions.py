"""Parameterized MySQL queries executed through SQLAlchemy Core."""


def get_user_from_request_1(connection, parameters):
    return connection.execute(
        """
            SELECT u.*
            FROM user_sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.token_hash = ?
              AND u.active = 1
              AND s.expires_at > ?
            LIMIT 1
        """,
        parameters,
    )


def create_user_session_1(connection, parameters):
    return connection.execute("DELETE FROM user_sessions WHERE expires_at <= ?", parameters)


def create_user_session_2(connection, parameters):
    return connection.execute(
        """
            INSERT INTO user_sessions(user_id, token_hash, created_at, expires_at)
            VALUES (?, ?, ?, ?)
        """,
        parameters,
    )


def delete_user_session_1(connection, parameters):
    return connection.execute("DELETE FROM user_sessions WHERE token_hash = ?", parameters)


def audit_action_1(connection, parameters):
    return connection.execute(
        """
            INSERT INTO audit_log(
                user_id, username, full_name, role,
                action, path, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        parameters,
    )


def count_active_admins_1(connection, parameters):
    return connection.execute(
        """
        SELECT COUNT(*) AS c
        FROM users
        WHERE role = 'ADMIN' AND active = 1
    """,
        parameters,
    )
