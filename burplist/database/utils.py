from burplist.database.models import Base
from scrapy.utils.project import get_project_settings
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine

settings = get_project_settings()


def db_connect() -> Engine:
    """
    Performs database connection using database settings from settings.py
    Returns sqlalchemy engine instance
    """
    return create_engine(settings.get('DATABASE_CONNECTION_STRING'))


def create_table(engine: Engine) -> None:
    Base.metadata.create_all(engine)
