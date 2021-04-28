import logging
import re
from typing import Tuple
from urllib.parse import urlencode

import scrapy
from burplist.items import ProductItem
from scrapy.loader import ItemLoader

logger = logging.getLogger(__name__)


class IShopChangiSpider(scrapy.Spider):
    """
    Parse data from site's API
    """
    name = 'ishopchangi'
    custom_settings = {'ROBOTSTXT_OBEY': False}

    BASE_URL = 'https://www.ishopchangi.com/bin/cagcommerce/webservices/v2/cag/products/search.json?'

    params = {
        'currentPage': 1,
        'query': '::cagCategory:/wine-and-spirits/beers:cagCategory:/wine-and-spirits/beers/stout:cagCategory:/wine-and-spirits/beers/cider:cagCategory:/wine-and-spirits/beers/craft-beer:cagCategory:/wine-and-spirits/beers/non-craft-beer:cagCollectionPoint:HOMEDELIVERYNONTRAVELLER:cagCollectionPoint:LANDSIDE',
        'categoryCodes': 'travel-electronics-chargers,beauty,food,Womens-fashion',
        'lang': 'en',
    }

    headers = {
        'referer': 'https://www.ishopchangi.com/en/category/wine-and-spirits/beers?' + urlencode({'cagCategory': {"/wine-and-spirits/beers/craft-beer": []}}),
    }

    def _get_product_name_quantity(self, raw_name: str) -> Tuple[str, int]:
        logger.info(f'raw_name = "{raw_name}"')

        # Ba Xian Tea Lager 3 Bottles Pack
        if 'Bottles Pack' in raw_name:
            quantity = int(re.search(r'\d+ ', raw_name).group())
            return raw_name, quantity

        # 6 Bottles Pack
        is_pack = re.search(r'\d+ Pack', raw_name)
        if is_pack:
            quantity = int(is_pack.group().split()[0])
            name = re.sub(is_pack.group(), '', raw_name)
            return name, quantity

        # La Chouffe Belgian Strong Golden Ale, 4x330ml
        is_ml = re.search(r'\d+x\d{3}ml', raw_name, flags=re.IGNORECASE)
        if is_ml:
            quantity = int(re.split('x', is_ml.group())[0])
            name = re.sub(is_ml.group(), '', raw_name)
            return name, quantity

        # LA TRAPPE TRIPEL BOTTLE 330ML*3
        is_multiply = re.search(r'\d{3}ml[*]\d+', raw_name, flags=re.IGNORECASE)
        if is_multiply:
            quantity = int(re.split(r'[*]', is_multiply.group())[-1])
            name = re.sub(is_multiply.group(), '', raw_name)
            return name, quantity

        # Lion City Meadery Hibiscus Blueberry Mead 330ml x 6
        is_ml_reverse = re.search(r'\d{3}ml x \d+', raw_name, flags=re.IGNORECASE)
        if is_ml_reverse:
            quantity = int(re.split('x', is_ml_reverse.group())[-1])
            name = re.sub(is_ml_reverse.group(), '', raw_name)
            return name, quantity

        return raw_name, 1

    def start_requests(self):
        url = self.BASE_URL + urlencode(self.params)
        yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)

    def parse(self, response):
        data = response.json()
        products = data['products']

        for product in products:
            loader = ItemLoader(item=ProductItem(), selector=product)

            name, quantity = self._get_product_name_quantity(product['name'])

            loader.add_value('vendor', self.name)
            loader.add_value('name', name)
            loader.add_value('price', product['price']['value'])
            loader.add_value('quantity', quantity)
            loader.add_value('url', response.urljoin(product['url']))
            yield loader.load_item()

        has_next_page = data['pagination']['currentPage'] < data['pagination']['totalPages']
        if has_next_page is True:
            self.params['currentPage'] += 1
            next_page = self.BASE_URL + urlencode(self.params)
            yield response.follow(next_page, callback=self.parse, headers=self.headers)
