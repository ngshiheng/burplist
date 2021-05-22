import logging
from typing import Any, Dict, List

from itemadapter import ItemAdapter
from scrapy import Spider
from scrapy.exceptions import DropItem
from sqlalchemy.orm import sessionmaker

from burplist.items import ProductItem
from burplist.models import Price, Product, create_table, db_connect

logger = logging.getLogger(__name__)


class DuplicatePricePipeline:
    """
    Check if a product already exist in pipeline and determine if it has price changes

    `url` and `quantity` is used to define the uniqueness of a product
    Using `url` alone isn't enough because the same URL (product) can have type of different `quantity`
    E.g.: "Pabst Blue Ribbon American Lager" can be of 'Single', '6 Packs' or 'Case of 24'

    Do not use `name` because name can change on a website
    Remove the product from the pipeline if it does not have any price changes
    """

    def __init__(self) -> None:
        """
        Initializes database connection and sessionmaker
        """
        engine = db_connect()
        create_table(engine)
        self.session = sessionmaker(bind=engine)

        self.prices = []

    def process_item(self, item: ProductItem, spider: Spider) -> ProductItem:
        assert spider
        adapter = ItemAdapter(item)

        url = adapter.get('url')
        quantity = adapter.get('quantity')
        price = adapter.get('price')

        if price is not None:
            current_price = float(price.amount)  # `.amount` is type of `<class 'decimal.Decimal'>`
        else:
            logger.warning(f'Item with <{url}> does not have a price.', extra=dict(url=url, quantity=quantity))
            raise DropItem(f'Dropping item because item <{url}> does not have a price.')

        session = self.session()
        try:
            existing_product = session.query(Product).filter_by(url=url, quantity=quantity).one_or_none()

        except Exception as exception:
            logger.exception('An unexpected error has occurred.', extra=dict(exception=exception, url=url, quantity=quantity))
            raise DropItem(f'Dropping item because item <{url}> because of an unexpected error.') from exception

        finally:
            session.close()

        if existing_product is not None:
            if existing_product.last_price == current_price:
                raise DropItem(f'Dropping item because item <{url}> has no price change.')

            price = dict(
                price=current_price,
                product_id=existing_product.id,
            )
            self.prices.append(price)
            raise DropItem(f'Dropping item <{url}> here after price update. We do not want duplicated products to be created in the following pipeline.')

        return item

    def close_spider(self, spider: Spider) -> None:
        """
        Saving all the scraped products and prices in bulk on spider close event
        We use `bulk_insert_mappings` instead of `bulk_save_objects` here as it accepts lists of plain Python dictionaries which results in less amount of overhead associated with instantiating mapped objects and assigning state to them, they are faster
        """
        session = self.session()

        try:
            prices = {frozenset(price.items()): price for price in self.prices}.values()  # Remove duplicated dict in a list. Reference: https://www.geeksforgeeks.org/python-removing-duplicate-dicts-in-list/
            session.bulk_insert_mappings(Price, prices)
            session.commit()
            logger.info(f'Saved {len(self.prices)} new prices for existing products to the database.')

        except Exception as error:
            logger.exception(error, extra=dict(spider=spider))
            session.rollback()
            raise

        finally:
            session.close()


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
        self.session = sessionmaker(bind=engine)

        self.products: List[Dict[str, Any]] = []

    def process_item(self, item: ProductItem, spider: Spider) -> ProductItem:
        """
        This method is called for every item pipeline component
        We save each product as a dict in `self.products` list so that it later be used for bulk saving
        """
        assert spider
        adapter = ItemAdapter(item)

        product = dict(
            name=adapter['name'],
            vendor=adapter['platform'],
            quantity=adapter['quantity'],
            url=adapter['url'],
            price=adapter['price'].amount
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
        session = self.session()

        try:
            products = {frozenset(product.items()): product for product in self.products}.values()  # Remove duplicated dict in a list.
            session.bulk_insert_mappings(Product, products, return_defaults=True)  # Set `return_defaults=True` so that PK (inserted one at a time) value is available for FK usage at another table

            prices = [dict(price=product['price'], product_id=product['id']) for product in products]
            session.bulk_insert_mappings(Price, prices)
            session.commit()

            logger.info(f'Saved {len(products)} new products in bulk operation to the database.')
            logger.info(f'Saved {len(prices)} new prices in bulk operation to the database.')

        except Exception as error:
            logger.exception(error, extra=dict(spider=spider))
            session.rollback()
            raise

        finally:
            session.close()
