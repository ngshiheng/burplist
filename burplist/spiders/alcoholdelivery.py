import logging
from urllib.parse import urlencode

import scrapy
from burplist.items import ProductItem
from burplist.utils.parsers import parse_brand
from scrapy.loader import ItemLoader

logger = logging.getLogger(__name__)


class AlcoholDeliverySpider(scrapy.Spider):
    """
    Parse data from site's API
    Site has 'Age Verification' modal
    Expect all of the product listed here are either in 'Single' or 'Keg'
    """
    name = 'alcoholdelivery'
    BASE_URL = 'https://www.alcoholdelivery.com.sg/api/fetchProducts?'

    params = {
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
        url = self.BASE_URL + urlencode(self.params)
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
                    # Skipping products which are out of stock
                    continue

                # Filter out product with 'Keg' inside the name
                if any(word in product['name'].lower() for word in ['keg', 'litre']):
                    continue

                loader = ItemLoader(item=ProductItem())

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
                loader.add_value('quantity', 1)  # NOTE: All scrapped item from this site are of quantity of 1

                loader.add_value('price', str(product['price'] + product['regular_express_delivery']['value']))
                yield loader.load_item()

            self.params['skip'] += 10
            next_page = self.BASE_URL + urlencode(self.params)
            yield response.follow(next_page, callback=self.parse)
