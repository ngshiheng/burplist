import datetime

from scrapy.utils.project import get_project_settings
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import column_property, relationship
from sqlalchemy.sql.expression import select

Base = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(get_project_settings().get('DATABASE_CONNECTION_STRING'))


def create_table(engine):
    Base.metadata.create_all(engine)


class Price(Base):
    __tablename__ = 'price'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False, index=True)
    product = relationship('Product', backref='prices', cascade='delete')

    price = Column('price', Float)
    updated_on = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self) -> str:
        return f'Price(price={self.price}, product={self.product.name})'


class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True)
    vendor = Column('vendor', String())
    name = Column('name', String())
    quantity = Column('quantity', Integer())
    url = Column('url', String())

    last_price = column_property(
        select([Price.price]).
        where(Price.product_id == id).
        order_by(Price.id.desc()).
        as_scalar()
    )

    def __repr__(self) -> str:
        return f'Product({self.name}, vendor={self.vendor})'
