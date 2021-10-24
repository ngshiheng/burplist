import re

import scrapy
from burplist.items import ProductLoader
from burplist.utils.parsers import parse_style


class ColdStorageSpider(scrapy.Spider):
    """Parse data from raw HTML"""

    name = 'coldstorage'
    start_urls = ['https://coldstorage.com.sg/beers-wines-spirits/beer-cider/craft-beers']

    def parse(self, response):
        """
        @url https://coldstorage.com.sg/beers-wines-spirits/beer-cider/craft-beers
        @returns items 1
        @returns requests 1 1
        @scrapes platform name url brand volume quantity price
        """
        products = response.xpath('//div[@class="product_box"]')

        for product in products:
            loader = ProductLoader(selector=product)

            name = product.xpath('.//div[@class="product_name "]/text()').get().strip()
            vendor = product.xpath('.//div[@class="category-name"]/b/text()').get().strip().title()

            loader.add_value('platform', self.name)
            loader.add_value('name', name)
            loader.add_value('url', response.urljoin(product.xpath('./a/@href').get()))

            loader.add_value('brand', vendor)
            loader.add_value('origin', None)
            loader.add_value('style', parse_style(name))

            loader.add_value('abv', None)
            loader.add_value('volume', name)
            loader.add_value('quantity', self.get_product_quantity(name))

            image_url = response.xpath('.//div[@class="product_images"]//img/@src').get()
            loader.add_value('image_url', image_url)

            loader.add_xpath('price', './/div[@data-price]/text()')
            yield loader.load_item()

        next_page = response.xpath('//li[@class="next"]/a/@href').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def get_product_quantity(raw_name: str) -> int:
        raw_quantity_with_name = re.search(r'(\d+s[x\s]+?\d+ml)', raw_name, flags=re.IGNORECASE)
        if raw_quantity_with_name:
            raw_quantity = raw_quantity_with_name.group().split(' ')
            return int(re.split(r's', raw_quantity[0], flags=re.IGNORECASE)[0])
        return 1
