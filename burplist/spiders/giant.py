import re
from typing import Generator

import scrapy

from burplist.items import ProductLoader
from burplist.locators import GiantLocator
from burplist.utils.parsers import parse_style


class GiantSpider(scrapy.Spider):
    """Scrape data from raw HTML

    https://giant.sg/beers-wines-spirits/beers-ciders
    """

    name = 'giant'
    start_urls = ['https://giant.sg/beers-wines-spirits/beers-ciders']

    def parse(self, response) -> Generator[scrapy.Request, None, None]:
        """
        @url https://giant.sg/beers-wines-spirits/beers-ciders
        @returns items 1
        @returns requests 1 1
        @scrapes platform name url quantity image_url price
        """
        products = response.xpath(GiantLocator.products)

        for product in products:

            name = product.xpath(GiantLocator.product_name).get()
            url = product.xpath(GiantLocator.product_url).get()

            loader = ProductLoader(selector=product)

            loader.add_value('platform', self.name)
            loader.add_value('name', name)
            loader.add_value('url', f"https://giant.sg{url}")

            loader.add_xpath('brand', GiantLocator.product_brand)
            loader.add_value('style', parse_style(name))
            loader.add_value('origin', None)

            loader.add_value('abv', None)
            loader.add_value('volume', name)
            loader.add_value('quantity', self.get_product_quantity(name))

            loader.add_xpath('image_url', GiantLocator.product_image_url)

            loader.add_xpath('price', GiantLocator.product_price)
            yield loader.load_item()

        has_next_page = response.xpath(GiantLocator.next_page).get()
        if has_next_page is not None:
            next_page = response.urljoin(has_next_page)
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def get_product_quantity(raw_name: str) -> int:
        raw_quantity_with_name = re.search(r'(\d+s[x\s]+?\d+ml)', raw_name, flags=re.IGNORECASE)
        if raw_quantity_with_name:
            raw_quantity = raw_quantity_with_name.group().split(' ')
            return int(re.split(r's', raw_quantity[0], flags=re.IGNORECASE)[0])
        return 1
