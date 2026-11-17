from alembic.config import Config
from alembic.script import ScriptDirectory
from app.core.config import PROJECT_DIR


def expected_revision():
    config = Config(str(PROJECT_DIR / "alembic.ini"))
    return ScriptDirectory.from_config(config).get_current_head()
