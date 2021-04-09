import re

import scrapy
from burplist.items import ProductItem
from scrapy.loader import ItemLoader


class ColdStorageSpider(scrapy.Spider):
    """
    Extract data from raw HTML

    BUG: "Somersby Seltzer Mango & Passionfruit Can 3s X"
    """
    name = 'coldstorage'
    start_urls = ['https://coldstorage.com.sg/beers-wines-spirits/beer-cider']

    def _get_product_quantity(self, raw_name: str) -> int:
        raw_quantity_with_name = re.search(r'(\d+s[x\s]+?\d+ml)', raw_name, flags=re.IGNORECASE)
        if raw_quantity_with_name:
            raw_quantity = raw_quantity_with_name.group().split(' ')
            return int(re.split(r's', raw_quantity[0], flags=re.IGNORECASE)[0])
        else:
            return 1

    def parse(self, response):
        products = response.xpath('//div[@class="product_box"]')

        for product in products:
            loader = ItemLoader(item=ProductItem(), selector=product)

            name = product.xpath('.//div[@class="product_name "]/text()').get().strip()
            vendor = product.xpath('.//div[@class="category-name"]/b/text()').get().strip().title()

            loader.add_value('vendor', self.name)
            loader.add_value('name', f'{vendor} {name}')
            loader.add_xpath('price', './/div[@data-price]/text()')
            loader.add_value('quantity', self._get_product_quantity(name))
            loader.add_value('url', response.urljoin(product.xpath('./a/@href').get()))
            yield loader.load_item()

        next_page = response.xpath('//li[@class="next"]/a/@href').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield response.follow(next_page, callback=self.parse)
