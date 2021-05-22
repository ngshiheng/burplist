from datetime import datetime

from scrapy.utils.project import get_project_settings
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import column_property, relationship
from sqlalchemy.sql.expression import select
from sqlalchemy.sql.schema import UniqueConstraint

settings = get_project_settings()

Base = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(settings.get('DATABASE_CONNECTION_STRING'))


def create_table(engine):
    Base.metadata.create_all(engine)


class Price(Base):
    __tablename__ = 'price'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False, index=True)
    product = relationship('Product', backref='prices', cascade='delete')

    price = Column('price', Float)
    updated_on = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f'Price(price={self.price}, product={self.product.name})'


class Product(Base):
    __tablename__ = 'product'
    __table_args__ = (UniqueConstraint('quantity', 'url'),)

    id = Column(Integer, primary_key=True)
    platform = Column(String())

    name = Column(String(), index=True)
    url = Column(String())

    brand = Column(String(), nullable=True, default=None)
    style = Column(String(), nullable=True, default=None)
    origin = Column(String(), nullable=True, default=None)

    abv = Column(Float(), nullable=True, default=None)
    volume = Column(Integer(), nullable=True, default=None)
    quantity = Column(Integer())

    created_on = Column(DateTime, default=datetime.utcnow)
    updated_on = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    last_price = column_property(
        select([Price.price]).
        where(Price.product_id == id).
        order_by(Price.id.desc()).
        limit(1).  # NOTE: We have to always limit this as 1 to prevent `CardinalityViolation: more than one row returned by a subquery used as an expression`
        as_scalar()
    )

    def __repr__(self) -> str:
        return f'Product({self.name}, platform={self.platform})'
