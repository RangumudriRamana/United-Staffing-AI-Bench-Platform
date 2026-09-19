from sqlalchemy.orm import DeclarativeBase

# Import the shared database dependency
from app.database.session import get_db


class Base(DeclarativeBase):
    """Base class for all ORM models."""


# Backward compatibility alias
# Older modules still import get_db_session from this file.
get_db_session = get_db