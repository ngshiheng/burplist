import re
from typing import Optional, Tuple

import scrapy
from burplist.items import ProductItem
from burplist.utils.parsers import parse_style
from scrapy.loader import ItemLoader


def _get_product_brand_and_origin(collection_name: str) -> Tuple[Optional[str], Optional[str]]:
    brand_origin_regex = re.search(r'(.*?) [\(](.*?)[\)]', collection_name)
    if brand_origin_regex:
        return brand_origin_regex.group(1), brand_origin_regex.group(2)

    return None, None


def _get_product_quantity(raw_name: str) -> int:
    raw_quantity_with_name = re.search(r'(\d+)(.*?)Pack', raw_name, flags=re.IGNORECASE)
    if raw_quantity_with_name:
        return int(raw_quantity_with_name.group(1))
    return 1


class TheGreatBeerExperimentSpider(scrapy.Spider):
    """
    Extract data from raw HTML
    """
    name = 'greatbeerexperiment'
    start_urls = ['https://greatbeerexperiment.com/collections']

    def parse(self, response):
        collections = response.xpath('//li[@class="site-nav--has-dropdown site-nav--active"]//li/a')
        for collection in collections:
            collection_name = collection.xpath('.//text()').get().strip()
            brand, origin = _get_product_brand_and_origin(collection_name)

            yield response.follow(collection, callback=self.parse_collection, meta={'brand': brand, 'origin': origin})

    def parse_collection(self, response):
        products = response.xpath('//div[@class="grid__item wide--one-fifth large--one-quarter medium-down--one-half"]')

        brand = response.meta['brand']
        origin = response.meta['origin']

        for product in products:
            loader = ItemLoader(item=ProductItem(), selector=product)
            loader.add_value('platform', self.name)

            name = product.xpath('.//p[@class="grid-link__title"]/text()').get()

            # Filter out merchandise
            if any(word in name.lower() for word in ['cap', 'tee', 'glass']):
                continue

            loader.add_value('name', name)
            loader.add_value('url', response.urljoin(product.xpath('.//a[@class="grid-link text-center"]/@href').get()))

            loader.add_value('brand', brand)
            loader.add_value('origin', origin)
            loader.add_value('style', parse_style(name))

            loader.add_value('abv', name)
            loader.add_value('volume', name)
            loader.add_value('quantity', _get_product_quantity(name))

            price = product.xpath('.//p[@class="grid-link__meta"]/text()').getall()[-1]
            loader.add_value('price', price)
            yield loader.load_item()

        # Recursively follow the link to the next page, extracting data from it
        next_page = response.xpath('//li/a[@title="Next »"]/@href').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse, meta={'brand': brand, 'origin': origin})