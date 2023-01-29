import re
from typing import Generator, Optional

import scrapy
from scrapy import Selector
from scrapy.exceptions import DropItem, IgnoreRequest

from burplist.items import ProductLoader
from burplist.locators import CraftBeerSGLocator


class CraftBeerSGSpider(scrapy.Spider):
    """Scrape data from raw HTML

    We get the beer product urls via a html script tag

    https://www.craftbeersg.com/
    """

    name = "craftbeersg"
    custom_settings = {"ROBOTSTXT_OBEY": False}
    start_urls = [f"https://www.craftbeersg.com/product-category/beer/page/{page_num}/" for page_num in range(1, 25)]

    def parse(self, response) -> Generator[scrapy.Request, None, None]:
        """
        @url https://www.craftbeersg.com/product-category/beer/
        @returns items 0
        @returns requests 1 20
        """
        raw_html = response.xpath(CraftBeerSGLocator.raw_html).get()
        if not raw_html:
            raise IgnoreRequest("Page not found.")
        html = raw_html.replace("\n", "").replace("\t", "").replace("\\", "")

        collections = Selector(text=html).xpath(CraftBeerSGLocator.beer_collection)
        yield from response.follow_all(collections, callback=self.parse_product_detail)

    def parse_product_detail(self, response) -> Generator[scrapy.Request, None, None]:
        name = response.xpath(CraftBeerSGLocator.product_name).get()
        url = response.request.url

        brand = response.xpath(CraftBeerSGLocator.product_brand).get()
        origin = response.xpath(CraftBeerSGLocator.product_origin).get()

        variants = response.xpath(CraftBeerSGLocator.product_variants)
        for product in variants:
            price = product.xpath(CraftBeerSGLocator.product_price).get()
            if not price:
                raise DropItem("Skip item with invalid price.")

            loader = ProductLoader(selector=product)

            loader.add_value("platform", self.name)
            loader.add_value("name", name)
            loader.add_value("url", url)

            loader.add_value("brand", brand)
            loader.add_value("origin", origin)
            loader.add_value("style", None)

            display_unit = product.xpath(CraftBeerSGLocator.product_display_unit).get()
            quantity, volume = self.get_product_quantity_volume(display_unit)

            loader.add_value("abv", None)
            loader.add_value("volume", volume)
            loader.add_value("quantity", quantity)

            loader.add_xpath("image_url", CraftBeerSGLocator.product_image_url)

            loader.add_value("price", price)

            yield loader.load_item()

    @staticmethod
    def get_product_quantity_volume(display_unit: str) -> tuple[int, Optional[str]]:
        """Parse product quantity from display_unit

        E.g. "6 Pack (6x 330ml)"""
        match = re.search(r"(\d+) Pack \((\d+)x (\d+)ml\)", display_unit)
        if not match:
            return 1, None

        quantity = int(match.group(2))
        volume = match.group(3)
        return quantity, volume
