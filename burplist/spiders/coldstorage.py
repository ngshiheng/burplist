import re
from typing import Generator

import scrapy

from burplist.items import ProductLoader
from burplist.locators import ColdStorageLocator
from burplist.utils.parsers import parse_brand, parse_style


class ColdStorageSpider(scrapy.Spider):
    """Scrape data from raw HTML

    https://coldstorage.com.sg/en/category/100001-100044-100386/1.html
    """

    name = "coldstorage"
    start_urls = ["https://coldstorage.com.sg/en/category/100001-100044-100386/1.html"]

    def parse(self, response) -> Generator[scrapy.Request, None, None]:
        """
        @url https://coldstorage.com.sg/en/category/100001-100044-100386/1.html
        @returns items 1
        @returns requests 0
        @scrapes platform name url brand quantity price
        """
        products = response.xpath(ColdStorageLocator.products)

        for product in products:
            name = product.xpath(ColdStorageLocator.product_name).get()

            loader = ProductLoader(selector=product)

            loader.add_value("platform", self.name)
            loader.add_value("name", name)
            loader.add_value("url", response.urljoin(product.xpath("./a/@href").get()))

            loader.add_value("brand", parse_brand(name))
            loader.add_value("style", parse_style(name))
            loader.add_value("origin", None)

            loader.add_value("abv", name)
            loader.add_value("volume", name)
            loader.add_value("quantity", self.get_product_quantity(name))

            loader.add_xpath("image_url", None)

            loader.add_xpath("price", ColdStorageLocator.product_price)
            yield loader.load_item()

        next_page = response.xpath(ColdStorageLocator.next_page).get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def get_product_quantity(raw_name: str) -> int:
        """Parse product quantity from item name

        E.g. "Session Ale Can 6sX375ml"
        """
        raw_quantity_with_name = re.search(
            r"(\d+s[x\s]+?\d+ml)", raw_name, flags=re.IGNORECASE
        )
        if raw_quantity_with_name:
            raw_quantity = raw_quantity_with_name.group().split(" ")
            return int(re.split(r"s", raw_quantity[0], flags=re.IGNORECASE)[0])
        return 1
