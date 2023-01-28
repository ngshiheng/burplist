import re
from typing import Generator

import scrapy

from burplist.items import ProductLoader
from burplist.locators import ThirstyLocator


class ThirstySpider(scrapy.Spider):
    """Scrape data from raw HTML

    https://www.thirsty.com.sg/
    """

    name = "thirsty"
    custom_settings = {"ROBOTSTXT_OBEY": False}
    start_urls = [
        f"https://www.thirsty.com.sg/collections/beer?page={page_num}"
        for page_num in range(1, 10)
    ]

    def parse(self, response) -> Generator[scrapy.Request, None, None]:
        """
        @url https://www.thirsty.com.sg/collections/beer
        @returns items 0
        @returns requests 1 24
        """
        collections = response.xpath(ThirstyLocator.beer_collection)
        yield from response.follow_all(collections, callback=self.parse_product_detail)

    def parse_product_detail(self, response) -> Generator[scrapy.Request, None, None]:
        name = response.xpath(ThirstyLocator.product_name).get()
        url = response.request.url

        brand = response.xpath(ThirstyLocator.product_brand).get()
        origin = response.xpath(ThirstyLocator.product_origin).get()
        style = response.xpath(ThirstyLocator.product_style).get()

        abv = response.xpath(ThirstyLocator.product_abv).get()

        image_url = response.xpath(ThirstyLocator.product_image_url).get()

        variants = response.xpath(ThirstyLocator.product_variants)
        for product in variants:
            display_unit = product.xpath(ThirstyLocator.product_display_unit).get()
            if not display_unit:
                continue

            loader = ProductLoader(selector=product)

            loader.add_value("platform", self.name)
            loader.add_value("name", name)
            loader.add_value("url", url)

            loader.add_value("brand", brand)
            loader.add_value("origin", origin)
            loader.add_value("style", style)

            quantity, volume = self.get_product_quantity_volume(display_unit)
            loader.add_value("abv", abv)
            loader.add_value("volume", volume)
            loader.add_value("quantity", quantity)

            loader.add_value("image_url", f"https:{image_url}")

            price = product.xpath(ThirstyLocator.product_price).get()
            loader.add_value("price", price)

            yield loader.load_item()

    @staticmethod
    def get_product_quantity_volume(display_unit: str) -> tuple[int, str]:
        quantity_volume = re.split(
            "x", display_unit, maxsplit=2, flags=re.IGNORECASE
        )  # "24 x 375ML". "x" could be upper case
        if len(quantity_volume) == 1:  # "375ML"
            assert isinstance(quantity_volume[0], str), type(quantity_volume)
            return 1, quantity_volume[0]

        return int(quantity_volume[0]), quantity_volume[1]
