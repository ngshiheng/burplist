
import logging

from itemadapter import ItemAdapter
from scrapy import Spider
from scrapy.exceptions import DropItem
from sqlalchemy.orm import sessionmaker

from burplist.items import ProductItem
from burplist.models import Price, Product, create_table, db_connect

logger = logging.getLogger(__name__)


class NewProductPricePipeline:
    """
    Main pipeline that save new products and their prices into database
    """

    def __init__(self):
        """
        Initializes database connection and sessionmaker
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)
        self.products = []
        self.prices = []

    def process_item(self, item: ProductItem, spider: Spider) -> ProductItem:
        """
        This method is called for every item pipeline component
        We save the Product object in self.products in a list so that it later be used for bulk saving
        """
        product = Product(
            name=item['name'],
            vendor=item['vendor'],
            quantity=item['quantity'],
            url=item['url'],
        )
        self.products.append(product)
        self.prices.append(item['price'].amount)

        return item

    def close_spider(self, spider):
        """
        Saving all the scraped products and prices in bulk on spider close event

        Sadly we currently have to use `return_defaults=True` while bulk saving Product objects which greatly reduces the performance gains of the bulk operation
        Though prices do get inserted to the DB in bulk

        Reference: https://stackoverflow.com/questions/36386359/sqlalchemy-bulk-insert-with-one-to-one-relation
        """
        session = self.Session()

        try:
            logger.info('Saving products in bulk operation to the database.')
            session.bulk_save_objects(self.products, return_defaults=True)  # Set `return_defaults=True` so that PK (inserted one at a time) value is available for FK usage at another table

            logger.info('Saving prices in bulk operation to the database.')
            prices = [Price(price=price, product_id=product.id) for product, price in zip(self.products, self.prices)]
            session.bulk_save_objects(prices)
            session.commit()

        except Exception as error:
            logger.exception(error, extra=dict(spider=spider))
            session.rollback()
            raise

        finally:
            session.close()


class DuplicatePricePipeline:
    """
    Check if a product already exist in pipeline and determine if it has price changes

    `url` and `quantity` is used to define the uniqueness of a product
    Using `url` alone isn't enough because the same URL (product) can have type of different `quantity`
    E.g.: "Pabst Blue Ribbon American Lager" can be of 'Single', '6 Packs' or 'Case of 24'

    Do not use `name` because name can change on a website
    Remove the product from the pipeline if it does not have any price changes
    """

    def __init__(self):
        """
        Initializes database connection and sessionmaker
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item: ProductItem, spider: Spider) -> ProductItem:
        adapter = ItemAdapter(item)
        session = self.Session()

        url = adapter.get('url')
        quantity = adapter.get('quantity')
        price = adapter.get('price')
        if price is not None:
            current_price = float(price.amount)  # `.amount` is type of `<class 'decimal.Decimal'>`
        else:
            raise DropItem(f'Dropping item because item <{url}> does not have a price.')

        existing_product = session.query(Product).filter_by(url=url, quantity=quantity).first()

        if existing_product is not None:
            if existing_product.last_price == current_price:
                raise DropItem(f'Dropping item because item <{url}> has no price change.')

            else:
                price = Price(
                    price=current_price,
                    product=existing_product,
                )

                try:
                    session.add(price)  # TODO: Use `bulk_update_mappings`
                    session.commit()

                except Exception as error:
                    logger.exception(error, extra=dict(item=item, spider=spider))
                    session.rollback()
                    raise

                finally:
                    session.close()

        session.close()
        return item
