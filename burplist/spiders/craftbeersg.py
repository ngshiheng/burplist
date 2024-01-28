from typing import Generator

import scrapy

from burplist.items import ProductLoader
from burplist.locators import CraftBeerSGLocator


class CraftBeerSGSpider(scrapy.Spider):
    """Scrape data from raw HTML

    We get the beer product urls via a html script tag

    https://www.craftbeersg.com/
    """

    name = "craftbeersg"
    custom_settings = {"ROBOTSTXT_OBEY": False}
    start_urls = ["https://www.craftbeersg.com/collections"]

    def parse(self, response) -> Generator[scrapy.Request, None, None]:
        """
        @url https://www.craftbeersg.com/collections
        @returns items 0
        @returns requests 1 8
        """
        collections = response.xpath(CraftBeerSGLocator.beer_collection)
        for collection in collections:
            style = collection.xpath(".//text()").get().strip()
            if style == "Everything Else":
                continue

            yield response.follow(collection, callback=self.parse_collection, meta={"style": style})

    def parse_collection(self, response) -> Generator[scrapy.Request, None, None]:
        products = response.xpath(CraftBeerSGLocator.products)
        style = response.meta["style"]

        for product in products:
            name, brand = self.get_product_name_and_brand(product.xpath(CraftBeerSGLocator.product_name_brand).get())

            loader = ProductLoader(selector=product)

            loader.add_value("platform", self.name)
            loader.add_value("name", name)
            loader.add_value(
                "url",
                response.urljoin(product.xpath(CraftBeerSGLocator.product_url).get()),
            )

            loader.add_value("brand", brand)
            loader.add_value("origin", None)
            loader.add_value("style", style)

            loader.add_value("abv", None)
            loader.add_value("volume", None)
            loader.add_value("quantity", 1)

            image_url = response.xpath(CraftBeerSGLocator.product_image_url).get()
            loader.add_value("image_url", f"https:{image_url}")

            print(name, brand, image_url)

            price = product.xpath(CraftBeerSGLocator.product_price).get()
            loader.add_value("price", price)
            yield loader.load_item()

        next_page = response.xpath(CraftBeerSGLocator.next_page).get()
        if next_page:
            yield response.follow(next_page, callback=self.parse, meta={"style": style})

    @staticmethod
    def get_product_name_and_brand(input_string: str) -> tuple[str, str]:
        brand, name = input_string.split("|", maxsplit=1)
        return name.strip(), brand.strip()
