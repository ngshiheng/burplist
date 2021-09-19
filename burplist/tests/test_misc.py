import unittest

from burplist.database.models import Price, Product
from burplist.database.utils import create_table
from burplist.utils.misc import remove_stale_products_prices
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class TestMisc(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine('sqlite:///:memory:')
        self.session = sessionmaker(bind=self.engine)
        create_table(self.engine)

        products = [
            dict(
                platform='burplist',
                name=f'name-{i}',
                url=f'https://burplist/product/{i}',
                quantity=24,
                price=10.90,
            )
            for i in range(5)
        ]

        with self.session.begin() as session:
            session.bulk_insert_mappings(Product, products, return_defaults=True)
            prices = [dict(price=product['price'], product_id=product['id']) for product in products]
            session.bulk_insert_mappings(Price, prices)

    def tearDown(self) -> None:
        Base.metadata.drop_all(self.engine)

    def test_prevent_remove_stale_products_from_deleting_all(self) -> None:
        self.assertRaises(AssertionError, remove_stale_products_prices, 0)
