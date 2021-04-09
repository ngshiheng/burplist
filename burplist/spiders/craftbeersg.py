import re
from typing import Tuple

import scrapy
from burplist.items import ProductItem
from scrapy.loader import ItemLoader


class CraftBeerSGSpider(scrapy.Spider):
    """
    Extract data from raw HTML
    Product quantity might come in a Pack of 6, Pack of 16, Pack of 24 and etc. https://craftbeersg.com/product-category/beer/page/36/
    """
    name = 'craftbeersg'
    start_urls = ['https://craftbeersg.com/product-category/beer']

    def _get_product_name_quantity(self, raw_name: str) -> Tuple[str, int]:
        name = raw_name.split('~', maxsplit=2)  # E.g.: "Magic Rock Brewing. Fantasma Gluten Free IPA ~ P198"
        name = re.sub('[()]', '', name[0])  # Remove all parenthesis

        if 'Pack of' in name:
            name, quantity = name.split('Pack of', maxsplit=2)
        elif 'Case of' in name:
            name, quantity = name.split('Case of', maxsplit=2)
        else:
            quantity = 1

        return name, int(quantity)

    def parse(self, response):
        products = response.xpath('//div[@class="product-inner"]')

        for product in products:
            loader = ItemLoader(item=ProductItem(), selector=product)

            raw_name = product.xpath('./a[@class="product-loop-title"]/h3/text()').get()
            name, quantity = self._get_product_name_quantity(raw_name)

            loader.add_value('vendor', self.name)
            loader.add_value('name', name)
            loader.add_xpath('price', './/span[@class="woocommerce-Price-amount amount"]/text()')
            loader.add_value('quantity', quantity)
            loader.add_xpath('url', './a[@class="product-loop-title"]/@href')
            yield loader.load_item()

        # Recursively follow the link to the next page, extracting data from it
        next_page = response.css('a.next.page-numbers').attrib.get('href')
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
