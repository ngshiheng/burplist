from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import column_property, relationship
from sqlalchemy.sql.expression import select
from sqlalchemy.sql.schema import UniqueConstraint

Base: Any = declarative_base()


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
    platform = Column(String(), nullable=False)

    name = Column(String(), index=True, nullable=False)
    url = Column(String(), nullable=False)

    brand = Column(String(), nullable=True, default=None)
    style = Column(String(), nullable=True, default=None)
    origin = Column(String(), nullable=True, default=None)

    abv = Column(Float(), nullable=True, default=None)
    volume = Column(Integer(), nullable=True, default=None)
    quantity = Column(Integer(), nullable=False)

    image_url = Column(String(), nullable=True, default=None)

    created_on = Column(DateTime, default=datetime.utcnow)
    updated_on = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    last_price = column_property(
        select([Price.price]).
        where(Price.product_id == id).
        order_by(Price.id.desc()).
        limit(1).  # NOTE: We have to always limit this as 1 to prevent `CardinalityViolation: more than one row returned by a subquery used as an expression`
        as_scalar(),
    )

    def __repr__(self) -> str:
        return f'Product({self.name}, platform={self.platform})'
