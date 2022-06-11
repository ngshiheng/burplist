import json
import logging
import re
from typing import Generator, Optional

import scrapy
from burplist.items import ProductLoader
from burplist.locators import TroubleBrewingLocator
from burplist.utils.const import SKIPPED_ITEMS
from burplist.utils.parsers import parse_style

logger = logging.getLogger(__name__)


class TroubleBrewingSpider(scrapy.Spider):
    """Parse data from raw HTML

    Starting URL is from a base URL which contains collections of beers,
    we then need to dive into each individual collection URL to obtain the product information

    We get the beer information via a html script tag as shown in the example below:
    <script>
    ...
    var meta = {"product":{"id":4468579795059,"gid":"gid://shopify/Product/4468579795059","vendor":"Trouble Brewing Store","type":"Beer","variants":[{"id":31829208989811,"price":7700,"name":"Middle Child Wheat Beer - 24 pack","public_title":"24 pack","sku":"TCWB24B"},{"id":32061886857331,"price":4200,"name":"Middle Child Wheat Beer - 12 pack","public_title":"12 pack","sku":"TCWB12B"},{"id":31829224194163,"price":2200,"name":"Middle Child Wheat Beer - 6 pack","public_title":"6 pack","sku":"TCWB6B"}]},"page":{"pageType":"product","resourceType":"product","resourceId":4468579795059},"page_view_event_id":"9e681da76f7007fc67a3a5a2fee2501bba0089fc71f880ef6fe820cce2fce5ee","cart_event_id":"34099f8e9fac4792e8758a189e2bda70923c0d854dc4067398d5a7b104e4a719"};
    ...
    </script>
    """

    name = 'troublebrewing'
    start_urls = ['https://troublebrewing.com/collections/trouble-beer-cider-hard-seltzer']

    def parse(self, response) -> Generator[scrapy.Request, None, None]:
        """
        @url https://troublebrewing.com/collections/trouble-beer-cider-hard-seltzer
        @returns requests 1
        """
        collections = response.xpath(TroubleBrewingLocator.beer_collection)
        yield from response.follow_all(collections, callback=self.parse_collection)

    def parse_collection(self, response) -> Generator[scrapy.Request, None, None]:
        """
        @url https://troublebrewing.com/collections/trouble-beer-cider-hard-seltzer/products/road-hog
        @returns items 1 3
        @returns requests 0 0
        @scrapes platform name url brand origin volume quantity image_url price
        """
        script_tag = response.xpath(TroubleBrewingLocator.script_tag).get()

        data_regex = re.search(r'\[\{(.*?)\]', script_tag)
        if data_regex:
            products = json.loads(data_regex.group())

            for product in products:
                name = product['name']

                if any(word in name.lower() for word in SKIPPED_ITEMS):
                    logger.info("Skipping non-beer item.")  # e.g. 'gift'
                    continue

                loader = ProductLoader()

                loader.add_value('platform', self.name)
                loader.add_value('name', name)
                loader.add_value('url', response.request.url)

                loader.add_value('brand', 'Trouble Brewing')
                loader.add_value('origin', 'Singapore')
                loader.add_value('style', parse_style(name))

                loader.add_value('abv', None)
                loader.add_value('volume', '330ml')
                loader.add_value('quantity', self.get_product_quantity(product['sku'], product['public_title']))

                image_url = response.xpath(TroubleBrewingLocator.product_image_url).get()
                loader.add_value('image_url', f'https:{image_url}')

                loader.add_value('price', product['price'] / 100)  # e.g. 7700 == $77.00
                yield loader.load_item()

    @staticmethod
    def get_product_quantity(sku: Optional[str], public_title: Optional[str] = None) -> int:
        if sku is None:
            return 24

        # Special case for "Trouble Brewing x @FEEDBENG Chinese New Year Gift Set"
        if public_title and 'Gift Set' in public_title:
            return 2

        # Special case for "Limited - Golden Pig Session IPA"
        if public_title and '24 pack' in public_title:
            return 24
        if public_title and '6 pack' in public_title:
            return 6

        # Normal case
        if sku.endswith('24B'):
            return 24
        if sku.endswith('12B'):
            return 12
        if sku.endswith('6B'):
            return 6
        if sku.startswith('SGBN') or sku.startswith('TCMX') or sku == '':
            return 24
        return 1
