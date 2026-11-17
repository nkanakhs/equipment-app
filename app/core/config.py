from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ELM_", env_file=PROJECT_DIR / ".env", extra="ignore"
    )
    storage_dir: Path = PROJECT_DIR / "storage"
    database_url: str
    session_days: int = Field(default=14, ge=1)
    cookie_secure: bool = False
    log_level: str = "INFO"


settings = Settings()
BASE_DIR = settings.storage_dir.expanduser().resolve()
STATIC_PATH = PROJECT_DIR / "app" / "static"
UPLOADS_PATH = BASE_DIR / "uploads"
EQUIPMENT_PHOTOS_PATH = UPLOADS_PATH / "equipment"
LOCATION_PHOTOS_PATH = UPLOADS_PATH / "locations"
DOCUMENTS_PATH = UPLOADS_PATH / "documents"
BACKUPS_PATH = BASE_DIR / "backups"


def ensure_storage():
    for path in (
        EQUIPMENT_PHOTOS_PATH,
        LOCATION_PHOTOS_PATH,
        DOCUMENTS_PATH,
        BACKUPS_PATH,
    ):
        path.mkdir(parents=True, exist_ok=True)
