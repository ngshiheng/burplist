import logging
import os
from urllib.parse import urlencode

import scrapy
from burplist.items import ProductItem
from burplist.utils.proxy import get_proxy_url
from scrapy.loader import ItemLoader

logger = logging.getLogger(__name__)


class LazadaSpider(scrapy.Spider):
    """
    Parse data from site's API
    We need to use rotating proxy to scrape from Lazada
    """
    name = 'lazada'
    custom_settings = {'ROBOTSTXT_OBEY': False, 'DOWNLOAD_DELAY': os.environ.get('LAZADA_DOWNLOAD_DELAY', 60)}
    BASE_URL = 'https://www.lazada.sg/shop-beer/?'

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
    }

    params = {
        'ajax': 'true',
        'rating': 4,  # We filter products that have at least 4 stars and above
        'page': 1,
    }

    def start_requests(self):
        url = self.BASE_URL + urlencode(self.params)
        yield scrapy.Request(url=get_proxy_url(url), callback=self.parse, headers=self.headers)

    def parse(self, response):
        data = response.json()

        products = data['mods']['listItems']

        # Stop sending requests when the REST API returns an empty array
        if products:
            for product in products:
                loader = ItemLoader(item=ProductItem(), selector=product)

                # We ignore the product if it has less than 20 reviews
                if int(product['review']) < 20:
                    continue

                loader.add_value('vendor', self.name)
                loader.add_value('name', product['name'])
                loader.add_value('price', product['price'])
                loader.add_value('quantity', 24)
                loader.add_value('url', product['productUrl'].replace('//', ''))
                yield loader.load_item()

            self.params['page'] += 1
            if int(data['mainInfo']['page']) <= int(data['mainInfo']['pageSize']):
                next_page = self.BASE_URL + urlencode(self.params)
                yield response.follow(get_proxy_url(next_page), callback=self.parse)
