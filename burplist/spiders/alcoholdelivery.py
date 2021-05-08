from urllib.parse import urlencode

import scrapy
from burplist.items import ProductItem
from scrapy.loader import ItemLoader


class AlcoholDeliverySpider(scrapy.Spider):
    """
    Parse data from site's API
    Site has 'Age Verification' modal
    Expect all of the product listed here are either in 'Single' or 'Keg'

    Additional product information:
    - Stock Availability
    - Style (name)
    - Volume (name)
    - ABV (name)
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
        'subParent': '',  # set as 'craft-beer' to only get craft beer data
        'type': 0,
    }

    def start_requests(self):
        url = self.BASE_URL + urlencode(self.params)
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        products = response.json()

        # Stop sending requests when the REST API returns an empty array
        if products:
            for product in products:

                # Filter out product with 'Keg' inside the name
                if any(word in product['name'].lower() for word in ['keg', 'litre']):
                    continue

                loader = ItemLoader(item=ProductItem(), selector=product)
                slug = product['slug']

                loader.add_value('vendor', self.name)
                loader.add_value('name', product['name'])
                loader.add_value('price', str(product['price'] + product['regular_express_delivery']['value']))
                loader.add_value('quantity', 1)  # NOTE: All scrapped item from this site are of quantity of 1
                loader.add_value('url', f'https://www.alcoholdelivery.com.sg/product/{slug}')
                yield loader.load_item()

            self.params['skip'] += 10
            next_page = self.BASE_URL + urlencode(self.params)
            yield response.follow(next_page, callback=self.parse)
