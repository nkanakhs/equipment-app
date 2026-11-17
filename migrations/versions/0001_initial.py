"""Initial MySQL schema for a fresh standalone installation."""
from alembic import op
from sqlalchemy import text
from app.db.models import Base

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    Base.metadata.create_all(connection)
    connection.execute(
        text("""INSERT INTO app_settings
        (id, application_name, library_name, organization_name, default_unit)
        VALUES (1, :application, :library, :organization, :unit)"""),
        dict(application="Equipment Library Manager", library="Βιβλιοθήκη Εξοπλισμού",
             organization="ΔΕΗ", unit="ΤΕΜ-ΘΗΣ"),
    )


def downgrade():
    raise RuntimeError("Restore a verified backup instead of dropping the schema.")
