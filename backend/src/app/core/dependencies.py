from app.core.config import Settings, get_settings
from app.database.session import get_db


def get_app_settings() -> Settings:
    """
    Shared dependency for accessing application settings.
    """
    return get_settings()