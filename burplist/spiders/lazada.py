import logging
import os
from urllib.parse import urlencode

import scrapy
from burplist.items import ProductItem
from burplist.utils.extractor import get_product_name_quantity
from burplist.utils.proxy import get_proxy_url
from scrapy.loader import ItemLoader

logger = logging.getLogger(__name__)


class LazadaSpider(scrapy.Spider):
    """
    Parse data from site's API
    We need to use rotating proxy to scrape from Lazada
    The API structure is similar to Red Mart
    """
    name = 'lazada'
    custom_settings = {'ROBOTSTXT_OBEY': False, 'DOWNLOAD_DELAY': os.environ.get('LAZADA_DOWNLOAD_DELAY', 60)}
    BASE_URL = 'https://www.lazada.sg/shop-beer/?'

    params = {
        'ajax': 'true',
        'rating': 4,  # We filter products that have at least 4 stars and above
        'page': 1,
    }

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'referer': f'{BASE_URL}page=' + str(params['page']),
    }

    def start_requests(self):
        url = self.BASE_URL + urlencode(self.params)
        yield scrapy.Request(url=get_proxy_url(url), callback=self.parse, headers=self.headers)

    def parse(self, response):
        data = response.json()
        if 'rgv587_flag' in data:
            raise ValueError(f'Rate limited by Lazada. URL <{response.request.url}>.')

        products = data['mods']['listItems']

        # Stop sending requests when the REST API returns an empty array
        if products:
            for product in products:
                loader = ItemLoader(item=ProductItem(), selector=product)

                name, quantity = get_product_name_quantity(product['name'])

                loader.add_value('vendor', self.name)
                loader.add_value('name', name)
                loader.add_value('price', product['price'])
                loader.add_value('quantity', quantity)
                loader.add_value('url', product['productUrl'].replace('//', ''))
                yield loader.load_item()

            self.params['page'] += 1
            if int(data['mainInfo']['page']) < 5:  # We only scrape up to 5 pages for Lazada. Anything beyond that are mostly trash
                next_page = self.BASE_URL + urlencode(self.params)
                yield response.follow(get_proxy_url(next_page), callback=self.parse, headers=self.headers)
