import re

import scrapy
from burplist.items import ProductItem
from scrapy.loader import ItemLoader


class ColdStorageSpider(scrapy.Spider):
    """
    Extract data from raw HTML
    """
    name = 'coldstorage'
    start_urls = ['https://coldstorage.com.sg/beers-wines-spirits/beer-cider']

    def _get_product_quantity(self, raw_name: str) -> int:
        if 'sX' in raw_name:
            raw_quantity_with_name = re.split('sX', raw_name, flags=re.IGNORECASE)[0]  # Example: "Super Dry Draft 6sX350ml"
            quantity = raw_quantity_with_name.split(' ')[-1]
            return int(quantity)
        else:
            return 1

    def parse(self, response):
        products = response.xpath('//div[@class="product_box"]')

        for product in products:
            loader = ItemLoader(item=ProductItem(), selector=product)

            name = product.xpath('.//div[@class="product_name "]/text()').get().strip()
            vendor = product.xpath('.//div[@class="category-name"]/b/text()').get().strip().title()

            loader.add_value('name', f'{vendor} {name}')
            loader.add_xpath('price', './/div[@data-price]/text()')
            loader.add_value('quantity', self._get_product_quantity(name))
            loader.add_value('url', response.urljoin(product.xpath('./a/@href').get()))
            yield loader.load_item()

        next_page = response.xpath('//li[@class="next"]/a/@href').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield response.follow(next_page, callback=self.parse)
