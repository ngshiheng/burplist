import json
import re
from typing import Optional

import scrapy
from burplist.items import ProductItem
from burplist.utils.parsers import parse_style
from scrapy.loader import ItemLoader


def _get_product_quantity(sku: Optional[str], public_title: Optional[str] = None) -> int:
    if sku is None:
        return 24

    # Special case for "Trouble Brewing x @FEEDBENG Chinese New Year Gift Set"
    if public_title and 'Gift Set' in public_title:
        return 2

    if sku.endswith('24B'):
        return 24
    if sku.endswith('12B'):
        return 12
    if sku.endswith('6B'):
        return 6
    if sku.startswith('SGBN') or sku.startswith('TCMX') or sku == '':
        return 24
    return 1


class TroubleBrewingSpider(scrapy.Spider):
    """
    Extract data from raw HTML
    Starting URL is from a base URL which contains collections of beers, we then need to dive into each individual collection URL to obtain the product information

    We get the beer information via a html script tag as shown in the example below:
    <script>
    ...
    var meta = {"product":{"id":4468579795059,"gid":"gid://shopify/Product/4468579795059","vendor":"Trouble Brewing Store","type":"Beer","variants":[{"id":31829208989811,"price":7700,"name":"Middle Child Wheat Beer - 24 pack","public_title":"24 pack","sku":"TCWB24B"},{"id":32061886857331,"price":4200,"name":"Middle Child Wheat Beer - 12 pack","public_title":"12 pack","sku":"TCWB12B"},{"id":31829224194163,"price":2200,"name":"Middle Child Wheat Beer - 6 pack","public_title":"6 pack","sku":"TCWB6B"}]},"page":{"pageType":"product","resourceType":"product","resourceId":4468579795059},"page_view_event_id":"9e681da76f7007fc67a3a5a2fee2501bba0089fc71f880ef6fe820cce2fce5ee","cart_event_id":"34099f8e9fac4792e8758a189e2bda70923c0d854dc4067398d5a7b104e4a719"};
    ...
    </script>
    """
    name = 'troublebrewing'
    start_urls = ['https://troublebrewing.com/collections/trouble-beer-cider-hard-seltzer']

    def parse(self, response):
        """
        @url https://troublebrewing.com/collections/trouble-beer-cider-hard-seltzer
        @returns requests 1
        """
        collections = response.xpath('//a[@class="product-link js-product-link"]')
        yield from response.follow_all(collections, callback=self.parse_collection)

    def parse_collection(self, response):
        """
        @url https://troublebrewing.com/collections/trouble-beer-cider-hard-seltzer/products/road-hog
        @returns items 1 3
        @returns requests 0 0
        @scrapes platform name url brand origin style volume quantity price
        """
        script_tag = response.xpath('//script[contains(.,"var meta")]/text()').get()

        data_regex = re.search(r'\[\{(.*?)\]', script_tag)
        if not data_regex:
            yield

        products = json.loads(data_regex.group())

        for product in products:
            loader = ItemLoader(item=ProductItem())
            loader.add_value('platform', self.name)

            name = product['name'].split('-', maxsplit=2)[0]
            loader.add_value('name', name)
            loader.add_value('url', response.request.url)

            loader.add_value('brand', 'Trouble Brewing')
            loader.add_value('origin', 'Singapore')
            loader.add_value('style', parse_style(name))

            loader.add_value('abv', None)
            loader.add_value('volume', '330ml')
            loader.add_value('quantity', _get_product_quantity(product['sku'], product['public_title']))

            loader.add_value('price', str(product['price'] / 100))  # E.g.: 7700 == $77.00
            yield loader.load_item()
