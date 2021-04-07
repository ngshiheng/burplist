import datetime

from scrapy.utils.project import get_project_settings
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(get_project_settings().get('DATABASE_CONNECTION_STRING'))


def create_table(engine):
    Base.metadata.create_all(engine)


class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True)
    vendor = Column('vendor', String())
    name = Column('name', String())
    quantity = Column('quantity', Integer())
    url = Column('url', String())


class Price(Base):
    __tablename__ = 'price'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'))
    price = Column('price', Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
