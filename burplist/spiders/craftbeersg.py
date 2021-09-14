import re
from typing import Tuple

import scrapy
from burplist.items import ProductItem
from scrapy.loader import ItemLoader


class CraftBeerSGSpider(scrapy.Spider):
    """
    Extract data from raw HTML
    Product quantity might come in a Pack of 6, Pack of 16, Pack of 24 and etc. https://craftbeersg.com/product-category/beer/page/36/

    # TODO: Extract `origin` information
    # TODO: Add contracts to `parse_collection`. Need to handle passing of `meta`
    """
    name = 'craftbeersg'
    start_urls = ['https://craftbeersg.com/product-category/beer/by-brewery/']

    def parse(self, response):
        """
        @url https://craftbeersg.com/product-category/beer/by-brewery/
        @returns requests 1
        """
        collections = response.xpath('//li[@class="cat-item cat-item-145 current-cat cat-parent"]//li/a')
        for collection in collections:
            brand = collection.xpath('./text()').get()
            yield response.follow(collection, callback=self.parse_collection, meta={'brand': brand})

    def parse_collection(self, response):
        products = response.xpath('//div[@class="product-inner"]')

        brand = response.meta['brand']

        for product in products:
            loader = ItemLoader(item=ProductItem(), selector=product)
            loader.add_value('platform', self.name)

            raw_name = product.xpath('.//a[@class="product-loop-title"]/h3/text()').get()
            name, quantity = self.get_product_name_quantity(raw_name)

            loader.add_value('name', name)

            url = response.urljoin(product.xpath('.//a[@class="product-loop-title"]/@href').get())
            loader.add_value('url', url)

            loader.add_value('brand', brand)
            loader.add_value('origin', None)
            loader.add_value('quantity', quantity)

            loader.add_xpath('price', './/span[@class="woocommerce-Price-amount amount"]//bdi/text()')

            yield scrapy.Request(
                url,
                callback=self.parse_product_detail,
                meta={'item': loader.load_item()},
                dont_filter=False,
            )

        # Recursively follow the link to the next page, extracting data from it
        next_page = response.css('a.next.page-numbers').attrib.get('href')
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_product_detail(self, response):
        loadernext = ItemLoader(item=response.meta['item'], response=response)

        descriptions = response.xpath('.//div[@class="description woocommerce-product-details__short-description"]//text()').getall()
        descriptions = ''.join(descriptions).split('\n')  # NOTE: To workaround case where the style, volume, and abv are separate element in an array

        description = next((string for string in descriptions if '|' in string))

        style, volume, abv = description.split('|', maxsplit=2)
        loadernext.add_value('style', style)
        loadernext.add_value('volume', volume)
        loadernext.add_value('abv', abv)

        yield loadernext.load_item()

    @staticmethod
    def get_product_name_quantity(raw_name: str) -> Tuple[str, int]:
        name = raw_name.split('~', maxsplit=2)  # E.g.: "Magic Rock Brewing. Fantasma Gluten Free IPA ~ P198"
        name = re.sub('[()]', '', name[0])  # Remove all parenthesis

        if 'Pack of' in name:
            name, quantity = name.split('Pack of', maxsplit=2)
        elif 'Case of' in name:
            name, quantity = name.split('Case of', maxsplit=2)
        else:
            quantity = 1

        return name, int(quantity)
