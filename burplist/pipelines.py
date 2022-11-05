import logging
from typing import Any

from itemadapter import ItemAdapter
from scrapy import Spider
from scrapy.exceptions import DropItem
from sqlalchemy.exc import ProgrammingError

from burplist.database.models import Price, Product
from burplist.database.utils import Session, create_table, db_connect
from burplist.items import ProductItem
from burplist.utils.const import MAINSTREAM_BEER_BRANDS, SKIPPED_ITEMS

logger = logging.getLogger(__name__)


class FiltersPipeline:
    """Pipeline to filter unwanted products"""

    def process_item(self, item: ProductItem, spider: Spider) -> ProductItem:
        """Drop non-craft beers items"""
        del spider  # Unused

        adapter = ItemAdapter(item)

        url = adapter['url']
        name = adapter['name']
        brand = adapter.get('brand')

        is_skipped_items = any(word.lower() in SKIPPED_ITEMS for word in name.split(' '))
        is_main_stream_beer = brand and brand.lower() in MAINSTREAM_BEER_BRANDS

        if is_main_stream_beer or is_skipped_items:
            raise DropItem(f'Dropping non-craft beer item <{url}>.')

        return item


class UpdatesPipeline:
    """Pipeline to update existing products information and add new prices

    If the product is yet to exist, skip to the next pipeline
    """

    def __init__(self):
        self.prices: list[dict[str, Any]] = []
        self.products_update: list[dict[str, Any]] = []

    def process_item(self, item: ProductItem, spider: Spider) -> ProductItem:
        """Update existing product information

        Also create a new price for existing products if the new price differs from the existing price

        `url` and `quantity` is used to define the uniqueness of a product
        Using `url` alone isn't enough because the same URL (product) can have type of different `quantity`
        e.g. "Pabst Blue Ribbon American Lager" can be of 'Single', '6 Packs' or 'Case of 24'

        We save each product as a dict in `self.products` list so that it later be used for bulk saving
        """
        del spider  # Unused

        adapter = ItemAdapter(item)

        url = adapter['url']
        quantity = adapter['quantity']
        current_price = adapter['price']

        session = Session()
        try:
            existing_product = session.query(Product).filter_by(url=url, quantity=quantity).one_or_none()

        except ProgrammingError as exception:
            logger.exception('An unexpected error has occurred.', extra=dict(exception=exception, url=url, quantity=quantity))
            raise DropItem(f'Dropping item <{url}> due to unexpected error.') from exception

        finally:
            session.close()

        if not existing_product:
            return item

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

        if existing_product.last_price != current_price.amount:
            price = dict(
                product_id=existing_product.id,
                price=current_price.amount,
            )
            self.prices.append(price)

        raise DropItem(f'Dropping item <{url}> after update to avoid creating duplicated products in the following pipeline.')

    def close_spider(self, spider: Spider) -> None:
        """Save all the scraped products and prices in bulk on spider close event

        We use `bulk_insert_mappings` instead of `bulk_save_objects` here as it accepts lists of plain Python dictionaries
        This results in less amount of overhead associated with instantiating mapped objects and assigning state to them, they are faster
        """
        with Session() as session:
            session.bulk_update_mappings(Product, self.products_update)
            logger.info(f'Updating {len(self.products_update)} existing products information')

            prices = {frozenset(price.items()): price for price in self.prices}.values()  # Remove duplicated dict in a list. Only works if all values in dict are hashable. Reference: https://www.geeksforgeeks.org/python-removing-duplicate-dicts-in-list/
            session.bulk_insert_mappings(Price, prices)
            logger.info(f'Creating {len(self.prices)} new prices for existing products')

            session.commit()

        if len(self.products_update) == 0:
            raise ValueError(f"No existing product information was updated for {spider.name}.")


class CreationPipeline:
    """Pipeline to create new products and prices"""

    def __init__(self):
        engine = db_connect()
        create_table(engine)
        self.products: list[dict[str, Any]] = []

    def process_item(self, item: ProductItem, spider: Spider) -> ProductItem:
        """Create new product"""
        del spider  # Unused

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
        """Save all the scraped products and prices in bulk on spider close event

        We currently have to use `return_defaults=True` while bulk saving Product objects
        This greatly reduces the performance gains of the bulk operation
        Though, prices do get inserted to the DB in bulk

        Reference: https://stackoverflow.com/questions/36386359/sqlalchemy-bulk-insert-with-one-to-one-relation
        """
        del spider  # Unused

        with Session() as session:
            products = {frozenset(product.items()): product for product in self.products}.values()  # Remove duplicated dict in a list
            session.bulk_insert_mappings(Product, products, return_defaults=True)  # Set `return_defaults=True` so that PK (inserted one at a time) value is available for FK usage at another table
            logger.info(f'Creating {len(products)} new products')

            prices = [dict(price=product['price'], product_id=product['id']) for product in products]
            session.bulk_insert_mappings(Price, prices)
            logger.info(f'Creating {len(prices)} new prices')

            session.commit()
