import logging
import re
from typing import Generator, Optional

import scrapy
from burplist.items import ProductLoader
from burplist.utils.const import SKIPPED_ITEMS
from burplist.utils.parsers import parse_style

logger = logging.getLogger(__name__)


class TheGreatBeerExperimentSpider(scrapy.Spider):
    """Parse data from raw HTML

    # TODO: Add contracts to `parse_collection`. Need to handle passing of `meta`
    """

    name = 'greatbeerexperiment'
    start_urls = ['https://greatbeerexperiment.com/collections']

    def parse(self, response) -> Generator[scrapy.Request, None, None]:
        """
        @url https://greatbeerexperiment.com/collections
        @returns requests 1
        """
        collections = response.xpath("//li[contains(@class,'brewery') and contains(./details, ' ')]//li/a")
        for collection in collections:
            collection_name = collection.xpath('.//text()').get().strip()
            brand, origin = self.get_product_brand_and_origin(collection_name)

            yield response.follow(collection, callback=self.parse_collection, meta={'brand': brand, 'origin': origin})

    def parse_collection(self, response) -> Generator[scrapy.Request, None, None]:
        products = response.xpath('//div[@class="productitem"]')

        brand = response.meta['brand']
        origin = response.meta['origin']

        for product in products:
            name = product.xpath('.//h2[@class="productitem--title"]/a/text()').get()

            if any(word in name.lower() for word in SKIPPED_ITEMS):
                logger.info("Skipping non-beer item.")  # e.g. 'cap', 'tee'
                continue

            loader = ProductLoader(selector=product)

            loader.add_value('platform', self.name)
            loader.add_value('name', name)
            loader.add_value('url', response.urljoin(product.xpath('.//h2[@class="productitem--title"]/a/@href').get()))

            loader.add_value('brand', brand)
            loader.add_value('origin', origin)
            loader.add_value('style', parse_style(name))

            loader.add_value('abv', name)
            loader.add_value('volume', name)
            loader.add_value('quantity', self.get_product_quantity(name))

            image_url = response.xpath('.//img[@class="productitem--image-primary" and @data-rimg-scale]/@src').get()  # NOTE: You need to disable JS to see this on inspect
            loader.add_value('image_url', f'https:{image_url}')

            price = product.xpath('.//div[@class="productitem--actions"]//div[@class="price__current--hidden"]/span[@class="money"]/text()').get()
            loader.add_value('price', price)
            yield loader.load_item()

        # Recursively follow the link to the next page, extracting data from it
        next_page = response.xpath('//li[@class="pagination--next"]/a/@href').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse, meta={'brand': brand, 'origin': origin})

    @staticmethod
    def get_product_brand_and_origin(collection_name: str) -> tuple[Optional[str], Optional[str]]:
        brand_origin_regex = re.search(r'(.*?) [\(](.*?)[\)]', collection_name)
        if brand_origin_regex:
            return brand_origin_regex.group(1), brand_origin_regex.group(2)

        return None, None

    @staticmethod
    def get_product_quantity(raw_name: str) -> int:
        raw_quantity_with_name = re.search(r'(\d+)(.*?)Pack', raw_name, flags=re.IGNORECASE)
        if raw_quantity_with_name:
            return int(raw_quantity_with_name.group(1))

        return 1
