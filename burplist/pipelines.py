from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class BurplistPipeline:
    def process_item(self, item, spider):
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
