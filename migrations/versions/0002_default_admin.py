"""Create the default administrator once, preserving existing accounts."""
from datetime import datetime
from alembic import op
from sqlalchemy import text
from app.core.security import hash_password

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        text("""INSERT INTO users
            (username, password_hash, full_name, role, active, created_at)
            SELECT :username, :password_hash, :full_name, 'ADMIN', 1, :created_at
            WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = :username)"""),
        {"username": "admin", "password_hash": hash_password("QWErty123!@#"),
         "full_name": "Administrator", "created_at": datetime.now().isoformat(timespec="seconds")},
    )


def downgrade():
    # Preserve the account and subsequent user changes.
    pass
