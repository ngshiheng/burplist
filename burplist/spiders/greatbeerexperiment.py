import re
from typing import Generator, Optional

import scrapy

from burplist.items import ProductLoader
from burplist.locators import TheGreatBeerExperimentLocator
from burplist.utils.parsers import parse_style


class TheGreatBeerExperimentSpider(scrapy.Spider):
    """Scrape data from raw HTML

    https://greatbeerexperiment.com/
    """

    name = "greatbeerexperiment"
    start_urls = ["https://greatbeerexperiment.com/collections"]

    def parse(self, response) -> Generator[scrapy.Request, None, None]:
        """
        @url https://greatbeerexperiment.com/collections
        @returns requests 1
        """
        collections = response.xpath(TheGreatBeerExperimentLocator.beer_collection)
        for collection in collections:
            collection_name = collection.xpath(".//text()").get().strip()
            brand, origin = self.get_product_brand_and_origin(collection_name)

            yield response.follow(collection, callback=self.parse_collection, meta={"brand": brand, "origin": origin})

    def parse_collection(self, response) -> Generator[scrapy.Request, None, None]:
        products = response.xpath(TheGreatBeerExperimentLocator.products)

        brand = response.meta["brand"]
        origin = response.meta["origin"]

        for product in products:
            name = product.xpath(TheGreatBeerExperimentLocator.product_name).get()

            loader = ProductLoader(selector=product)

            loader.add_value("platform", self.name)
            loader.add_value("name", name)
            loader.add_value("url", response.urljoin(product.xpath(TheGreatBeerExperimentLocator.product_url).get()))

            loader.add_value("brand", brand)
            loader.add_value("origin", origin)
            loader.add_value("style", parse_style(name))

            loader.add_value("abv", name)
            loader.add_value("volume", name)
            loader.add_value("quantity", self.get_product_quantity(name))

            image_url = response.xpath(TheGreatBeerExperimentLocator.product_image_url).get()  # NOTE: You need to disable JS to see this on inspect
            loader.add_value("image_url", f"https:{image_url}")

            price = product.xpath(TheGreatBeerExperimentLocator.product_price).get()
            loader.add_value("price", price)
            yield loader.load_item()

        next_page = response.xpath(TheGreatBeerExperimentLocator.next_page).get()
        if next_page:
            yield response.follow(next_page, callback=self.parse, meta={"brand": brand, "origin": origin})

    @staticmethod
    def get_product_brand_and_origin(collection_name: str) -> tuple[Optional[str], Optional[str]]:
        brand_origin_regex = re.search(r"(.*?) [\(](.*?)[\)]", collection_name)
        if brand_origin_regex:
            return brand_origin_regex.group(1), brand_origin_regex.group(2)

        return None, None

    @staticmethod
    def get_product_quantity(raw_name: str) -> int:
        raw_quantity_with_name = re.search(r"(\d+)(.*?)Pack", raw_name, flags=re.IGNORECASE)
        if raw_quantity_with_name:
            return int(raw_quantity_with_name.group(1))

        return 1
