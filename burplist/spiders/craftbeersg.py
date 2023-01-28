import re
from typing import Optional

import scrapy
from scrapy import Selector

from burplist.items import ProductLoader
from burplist.locators import CraftBeerSGLocator


class CraftBeerSGSpider(scrapy.Spider):
    """Scrape data from raw HTML

    We get the beer product urls via a html script tag

    https://www.craftbeersg.com/
    """

    name = "craftbeersg"
    custom_settings = {"ROBOTSTXT_OBEY": False}
    start_urls = [
        f"https://www.craftbeersg.com/product-category/beer/page/{page_num}/"
        for page_num in range(1, 25)
    ]

    def parse(self, response):
        """
        @url https://www.craftbeersg.com/product-category/beer/
        @returns items 0
        @returns requests 1 20
        """
        raw_html = response.xpath(CraftBeerSGLocator.raw_html).get()
        html = raw_html.replace("\n", "").replace("\t", "").replace("\\", "")

        collections = Selector(text=html).xpath(CraftBeerSGLocator.beer_collection)
        yield from response.follow_all(collections, callback=self.parse_product_detail)

    def parse_product_detail(self, response):
        name = response.xpath(CraftBeerSGLocator.product_name).get()
        url = response.request.url

        brand = response.xpath(CraftBeerSGLocator.product_brand).get()
        origin = response.xpath(CraftBeerSGLocator.product_origin).get()

        variants = response.xpath(CraftBeerSGLocator.product_variants)
        for product in variants:
            display_unit = product.xpath(CraftBeerSGLocator.product_display_unit).get()
            if not display_unit:
                continue

            loader = ProductLoader(selector=product)

            loader.add_value("platform", self.name)
            loader.add_value("name", name)
            loader.add_value("url", url)

            loader.add_value("brand", brand)
            loader.add_value("origin", origin)
            loader.add_value("style", None)

            quantity, volume = self.get_product_quantity_volume(display_unit)
            loader.add_value("abv", None)
            loader.add_value("volume", volume)
            loader.add_value("quantity", quantity)

            loader.add_xpath("image_url", CraftBeerSGLocator.product_image_url)

            loader.add_xpath("price", CraftBeerSGLocator.product_price)

            yield loader.load_item()

    @staticmethod
    def get_product_quantity_volume(display_unit: str) -> tuple[int, Optional[str]]:
        match = re.search(r"(\d+) Pack \((\d+)x (\d+)ml\)", display_unit)
        if not match:
            return 1, None

        quantity = int(match.group(2))
        volume = match.group(3)
        return quantity, volume
