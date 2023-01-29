from scrapy.utils.project import get_project_settings
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.session import sessionmaker

from burplist.database.models import Base

settings = get_project_settings()


def db_connect() -> Engine:
    """Performs database connection using database settings from settings.py"""
    db_connection_string = settings.get("DATABASE_CONNECTION_STRING")
    assert db_connection_string, "DATABASE_CONNECTION_STRING is invalid."
    return create_engine(db_connection_string)


def create_table(engine: Engine) -> None:
    """Creates the database table for the classes defined in the ORM.

    It takes an SQLAlchemy Engine object as an argument and creates the table for all classes that inherit from the Base class.
    """
    Base.metadata.create_all(engine)


# NOTE: https://stackoverflow.com/questions/36090055/sqlalchemy-best-practices-when-how-to-configure-a-scoped-session
Session = scoped_session(sessionmaker(bind=db_connect()))
