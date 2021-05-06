import logging
import os
import re
from typing import Tuple
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
    The API structure is similar to Red Mart
    """
    name = 'lazada'
    custom_settings = {'ROBOTSTXT_OBEY': False, 'DOWNLOAD_DELAY': os.environ.get('LAZADA_DOWNLOAD_DELAY', 120)}
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

    def _get_product_name_quantity(self, raw_name: str) -> Tuple[str, int]:
        logger.info(f'raw_name = "{raw_name}"')

        # Hite Jinro Extra Cold Beer Single Carton
        if 'carton' in raw_name.lower():
            return raw_name, 24

        # Carlsberg Danish Pilsner Beer Can 490ml (Pack of 24) Green Tab
        is_pack = re.search(r'Pack of \d+', raw_name, flags=re.IGNORECASE)
        if is_pack:
            quantity = int(is_pack.group().split()[-1])
            name = re.sub(is_pack.group(), '', raw_name)
            return name, quantity

        # Tiger Lager Beer Can 40x320ml, Guinness Foreign Extra Stout 24 x 500ml
        is_ml = re.search(r'\d+\s?x\s?\d{3}ml', raw_name, flags=re.IGNORECASE)
        if is_ml:
            quantity = int(re.split('x', is_ml.group(), flags=re.IGNORECASE)[0])
            name = re.sub(is_ml.group(), '', raw_name)
            return name, quantity

        # Heineken Beer 330ml x 24 can
        is_ml_reverse = re.search(r'\d{3}ml\s?x\s?\d+', raw_name, flags=re.IGNORECASE)
        if is_ml_reverse:
            quantity = int(re.split('x', is_ml_reverse.group(), flags=re.IGNORECASE)[-1])
            name = re.sub(is_ml_reverse.group(), '', raw_name)
            return name, quantity

        # Blue Moon Belgian White Wheat Ale 355ml x 24 Bottles
        is_pack = re.search(r'\d+(?:[A-Za-z\s]|\s)+Bottles', raw_name, flags=re.IGNORECASE)
        if is_pack:
            quantity = int(is_pack.group().split()[0])
            name = re.sub(is_pack.group(), '', raw_name)
            return name, quantity

        # San Miguel Pale Pilsen Can (24 cans x 330ml)
        is_cans = re.search(r'\d+ Cans', raw_name, flags=re.IGNORECASE)
        if is_cans:
            quantity = int(is_cans.group().split()[0])
            name = re.sub(is_cans.group(), '', raw_name)
            return name, quantity

        return raw_name, 1

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

                name, quantity = self._get_product_name_quantity(product['name'])

                loader.add_value('vendor', self.name)
                loader.add_value('name', name)
                loader.add_value('price', product['price'])
                loader.add_value('quantity', quantity)
                loader.add_value('url', product['productUrl'].replace('//', ''))
                yield loader.load_item()

            self.params['page'] += 1
            if int(data['mainInfo']['page']) < 5:  # We only scrape up to 5 pages for Lazada. Anything beyond that are mostly trash
                next_page = self.BASE_URL + urlencode(self.params)
                yield response.follow(get_proxy_url(next_page), callback=self.parse)
