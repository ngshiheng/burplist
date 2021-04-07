from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from sqlalchemy.orm import sessionmaker

from burplist.models import Price, Product, create_table, db_connect


class BurplistPipeline:
    def __init__(self):
        """
        Initializes database connection and sessionmaker
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        """
        This method is called for every item pipeline component
        """
        session = self.Session()
        product = Product()
        price = Price()

        product.name = item['name']
        product.quantity = item['quantity']
        product.vendor = item['vendor']
        product.url = item['url']
        price.price = item['price']

        try:
            session.add(product)
            session.commit()

        except Exception:
            session.rollback()
            raise

        finally:
            session.close()

        return item


class DuplicatesPipeline:
    def __init__(self):
        self.product_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter['name'] in self.product_seen:
            raise DropItem(f'Duplicate item found: {item!r}')
        else:
            self.product_seen.add(adapter['name'])
            return item
