import logging
from typing import Any

from itemadapter import ItemAdapter
from scrapy import Spider
from scrapy.exceptions import DropItem
from sqlalchemy.exc import ProgrammingError

from burplist.database.models import Price, Product
from burplist.database.utils import Session, create_table, db_connect
from burplist.items import ProductItem

logger = logging.getLogger(__name__)


class ExistingProductPricePipeline:
    """
    Update existing products information
    Create a new price for existing products if the new price differs from the existing price

    `url` and `quantity` is used to define the uniqueness of a product
    Using `url` alone isn't enough because the same URL (product) can have type of different `quantity`
    e.g. "Pabst Blue Ribbon American Lager" can be of 'Single', '6 Packs' or 'Case of 24'

    Do not use `name` because name can change on a website
    """

    def __init__(self) -> None:
        """
        Initializes database connection and sessionmaker
        """
        self.prices: list[dict[str, Any]] = []
        self.products_update: list[dict[str, Any]] = []

    def process_item(self, item: ProductItem, spider: Spider) -> ProductItem:
        assert spider
        adapter = ItemAdapter(item)

        url = adapter['url']
        quantity = adapter['quantity']
        current_price = adapter['price']

        session = Session()
        try:
            existing_product = session.query(Product).filter_by(url=url, quantity=quantity).one_or_none()

        except ProgrammingError as exception:
            logger.exception('An unexpected error has occurred.', extra=dict(exception=exception, url=url, quantity=quantity))
            raise DropItem(f'Dropping item because item <{url}> because of an unexpected error.') from exception

        finally:
            session.close()

        if existing_product is not None:
            # Always update information for existing products
            product_to_update = dict(
                id=existing_product.id,
                name=adapter.get('name'),

                brand=adapter.get('brand'),
                style=adapter.get('style'),
                origin=adapter.get('origin'),

                abv=adapter.get('abv'),
                volume=adapter.get('volume'),

                image_url=adapter.get('image_url'),
            )
            self.products_update.append(product_to_update)

            # Create new price object for the product
            if existing_product.last_price != current_price.amount:
                price = dict(
                    product_id=existing_product.id,
                    price=current_price.amount,
                )
                self.prices.append(price)

            raise DropItem(f'Dropping item <{url}> here after update. We do not want duplicated products to be created in the following pipeline.')

        return item

    def close_spider(self, spider: Spider) -> None:
        """
        Saving all the scraped products and prices in bulk on spider close event
        We use `bulk_insert_mappings` instead of `bulk_save_objects` here as it accepts lists of plain Python dictionaries which results in less amount of overhead associated with instantiating mapped objects and assigning state to them, they are faster
        """
        assert spider

        with Session() as session:
            session.bulk_update_mappings(Product, self.products_update)
            logger.info(f'Updated {len(self.products_update)} existing products information in bulk.')

            prices = {frozenset(price.items()): price for price in self.prices}.values()  # Remove duplicated dict in a list. Only works if all values in dict are hashable. Reference: https://www.geeksforgeeks.org/python-removing-duplicate-dicts-in-list/
            session.bulk_insert_mappings(Price, prices)
            logger.info(f'Created {len(self.prices)} new prices in bulk for existing products to the database.')

            session.commit()

        if len(self.products_update) == 0:
            raise ValueError(f"No existing product information was updated for {spider.name}.")


class NewProductPricePipeline:
    """
    Main pipeline that saves new products and their prices into database
    """

    def __init__(self) -> None:
        """
        Initializes database connection and sessionmaker
        """
        engine = db_connect()
        create_table(engine)
        self.products: list[dict[str, Any]] = []

    def process_item(self, item: ProductItem, spider: Spider) -> ProductItem:
        """
        This method is called for every item pipeline component
        We save each product as a dict in `self.products` list so that it later be used for bulk saving
        """
        assert spider
        adapter = ItemAdapter(item)

        product = dict(
            platform=adapter['platform'],

            name=adapter['name'],
            url=adapter['url'],

            brand=adapter.get('brand'),
            style=adapter.get('style'),
            origin=adapter.get('origin'),

            abv=adapter.get('abv'),
            volume=adapter.get('volume'),
            quantity=adapter.get('quantity'),

            image_url=adapter.get('image_url'),

            price=adapter['price'].amount,
        )

        self.products.append(product)

        return item

    def close_spider(self, spider: Spider) -> None:
        """
        Saving all the scraped products and prices in bulk on spider close event

        Sadly we currently have to use `return_defaults=True` while bulk saving Product objects which greatly reduces the performance gains of the bulk operation
        Though prices do get inserted to the DB in bulk

        Reference: https://stackoverflow.com/questions/36386359/sqlalchemy-bulk-insert-with-one-to-one-relation
        """
        assert spider

        with Session() as session:
            products = {frozenset(product.items()): product for product in self.products}.values()  # Remove duplicated dict in a list
            session.bulk_insert_mappings(Product, products, return_defaults=True)  # Set `return_defaults=True` so that PK (inserted one at a time) value is available for FK usage at another table
            logger.info(f'Saved {len(products)} new products in bulk operation to the database.')

            prices = [dict(price=product['price'], product_id=product['id']) for product in products]
            session.bulk_insert_mappings(Price, prices)
            logger.info(f'Saved {len(prices)} new prices in bulk operation to the database.')

            session.commit()
