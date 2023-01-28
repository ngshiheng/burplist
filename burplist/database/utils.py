from scrapy.utils.project import get_project_settings
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.session import sessionmaker

from burplist.database.models import Base

settings = get_project_settings()


def db_connect() -> Engine:
    """Performs database connection using database settings from settings.py"""
    return create_engine(settings.get("DATABASE_CONNECTION_STRING"))


def create_table(engine: Engine) -> None:
    Base.metadata.create_all(engine)


# NOTE: https://stackoverflow.com/questions/36090055/sqlalchemy-best-practices-when-how-to-configure-a-scoped-session
Session = scoped_session(sessionmaker(bind=db_connect()))
