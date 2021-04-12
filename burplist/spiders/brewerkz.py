import re

import scrapy
from burplist.items import ProductItem
from scrapy.loader import ItemLoader


class BrewerkzSpider(scrapy.Spider):
    """
    Extract data from raw HTML
    """
    name = 'brewerkz'
    start_urls = ['http://store.brewerkz.com/330ml-beer-can']

    def _get_product_quantity(self, raw_name: str) -> int:
        raw_quantity_with_name = re.search(r'\d+ x \d+ml', raw_name, flags=re.IGNORECASE)
        if raw_quantity_with_name:
            raw_quantity = re.split(r'x', raw_quantity_with_name.group(), flags=re.IGNORECASE)
            return int(raw_quantity[0])
        else:
            return 1

    def parse(self, response):
        products = response.xpath('//li[@class="product"]')

        for product in products:
            loader = ItemLoader(item=ProductItem(), selector=product)

            name = product.xpath('.//h4[@class="card-title"]/a/text()').get()

            loader.add_value('vendor', self.name)
            loader.add_value('name', f'Brewerkz {name}')
            loader.add_xpath('price', './/span[@class="price price--withTax price--main"]')
            loader.add_value('quantity', self._get_product_quantity(name))
            loader.add_xpath('url', './/h4[@class="card-title"]/a/@href')
            yield loader.load_item()

        next_page = response.xpath('//li[@class="pagination-item pagination-item--next"]/a/@href').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield response.follow(next_page, callback=self.parse)
