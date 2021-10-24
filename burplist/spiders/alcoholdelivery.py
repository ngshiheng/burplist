import logging
from typing import Any
from urllib.parse import urlencode

import scrapy
from burplist.items import ProductLoader
from burplist.utils.parsers import parse_brand

logger = logging.getLogger(__name__)


class AlcoholDeliverySpider(scrapy.Spider):
    """Parse data from REST API

    Site has 'Age Verification' modal
    Expect all of the product listed here are either in 'Single' or 'Keg'
    All scrapped item from this site are of quantity of 1
    """

    name = 'alcoholdelivery'
    base_url = 'https://www.alcoholdelivery.com.sg/api/fetchProducts?'

    params: dict[str, Any] = {
        'filter': 'all',
        'keyword': '',
        'limit': 10,
        'parent': 'beer-cider',
        'productList': 1,
        'skip': 0,  # Starting page
        'subParent': 'craft-beer',  # set as 'craft-beer' to only get craft beer data
        'type': 0,
    }

    def start_requests(self):
        url = self.base_url + urlencode(self.params)
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """
        @url https://www.alcoholdelivery.com.sg/api/fetchProducts?filter=all&keyword=&limit=10&parent=beer-cider&productList=1&skip=0&subParent=craft-beer&type=0
        @returns items 1 10
        @returns requests 1
        @scrapes platform name url origin style abv volume quantity price
        """
        products = response.json()

        # Stop sending requests when the REST API returns an empty array
        if products:
            for product in products:
                if product['quantity'] < 1:
                    continue

                # Filter out product with 'Keg' inside the name
                if any(word in product['name'].lower() for word in ['keg', 'litre']):
                    continue

                loader = ProductLoader()

                loader.add_value('platform', self.name)

                name = product['name']
                slug = product['slug']
                loader.add_value('name', name)
                loader.add_value('url', f'https://www.alcoholdelivery.com.sg/product/{slug}')

                short_description = product['shortDescription']
                origin, style, abv = short_description.split(',')

                loader.add_value('brand', parse_brand(product['name']))
                loader.add_value('origin', origin)
                loader.add_value('style', style)

                loader.add_value('abv', abv)
                loader.add_value('volume', name)
                loader.add_value('quantity', 1)

                image_url = product.get('imageFiles')[0]['source']
                loader.add_value('image_url', f'https://www.alcoholdelivery.com.sg/products/i/{image_url}')

                loader.add_value('price', product['price'] + product['regular_express_delivery']['value'])
                yield loader.load_item()

            self.params['skip'] += 10
            next_page = self.base_url + urlencode(self.params)
            yield response.follow(next_page, callback=self.parse)
