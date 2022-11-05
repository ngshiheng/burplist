import re
from typing import Any, Generator
from urllib.parse import urlencode

import scrapy

from burplist.items import ProductLoader
from burplist.utils.parsers import parse_style


class IShopChangiSpider(scrapy.Spider):
    """Scrape data from iShopChangi API

    Requires specific `referer` in the request header to work

    https://www.ishopchangi.com/en/home
    """

    name = 'ishopchangi'
    custom_settings = {'ROBOTSTXT_OBEY': False}

    base_url = 'https://www.ishopchangi.com/bin/cagcommerce/webservices/v2/cag/products/search.json?'

    params: dict[str, Any] = {
        'currentPage': 0,
        'query': '::cagCategory:/wine-and-spirits/beers:cagCategory:/wine-and-spirits/beers/stout:cagCategory:/wine-and-spirits/beers/cider:cagCategory:/wine-and-spirits/beers/craft-beer:cagCategory:/wine-and-spirits/beers/non-craft-beer:cagCollectionPoint:HOMEDELIVERYNONTRAVELLER:cagCollectionPoint:LANDSIDE',
        'categoryCodes': 'travel-electronics-chargers,beauty,food,Womens-fashion',
        'lang': 'en',
    }

    headers = {
        'referer': 'https://www.ishopchangi.com/en/category/wine-and-spirits/beers?' + urlencode({'cagCategory': {'/wine-and-spirits/beers/craft-beer': []}}),
    }

    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        url = self.base_url + urlencode(self.params)
        yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)

    def parse(self, response) -> Generator[scrapy.Request, None, None]:
        """
        @url https://www.ishopchangi.com/bin/cagcommerce/webservices/v2/cag/products/search.json?currentPage=0&query=%3A%3AcagCategory%3A%2Fwine-and-spirits%2Fbeers%3AcagCategory%3A%2Fwine-and-spirits%2Fbeers%2Fstout%3AcagCategory%3A%2Fwine-and-spirits%2Fbeers%2Fcider%3AcagCategory%3A%2Fwine-and-spirits%2Fbeers%2Fcraft-beer%3AcagCategory%3A%2Fwine-and-spirits%2Fbeers%2Fnon-craft-beer%3AcagCollectionPoint%3AHOMEDELIVERYNONTRAVELLER%3AcagCollectionPoint%3ALANDSIDE&categoryCodes=travel-electronics-chargers%2Cbeauty%2Cfood%2CWomens-fashion&lang=en
        @returns items 1
        @returns requests 1 1
        @scrapes platform name url brand quantity price
        """
        data = response.json()
        products = data['products']

        for product in products:
            name = product['name']
            quantity = self.get_product_quantity(name)

            loader = ProductLoader()

            loader.add_value('platform', self.name)
            loader.add_value('name', name)
            loader.add_value('url', response.urljoin(product['url']))

            loader.add_value('brand', product['manufacturer'])
            loader.add_value('origin', None)
            loader.add_value('style', parse_style(product['productDisplayName']))

            loader.add_value('abv', None)
            loader.add_value('volume', name)
            loader.add_value('quantity', quantity)

            image_url = product.get('imageUrl')
            loader.add_value('image_url', image_url)

            loader.add_value('price', product['price']['value'])
            yield loader.load_item()

        has_next_page = data['pagination']['currentPage'] < data['pagination']['totalPages']
        if has_next_page is True:
            self.params['currentPage'] += 1
            next_page = self.base_url + urlencode(self.params)
            yield response.follow(next_page, callback=self.parse, headers=self.headers)

    @staticmethod
    def get_product_quantity(raw_name: str) -> int:
        assert isinstance(raw_name, str)

        # "Ba Xian Tea Lager 3 Bottles Pack"
        if 'Bottles Pack' in raw_name:
            is_bottles_pack = re.search(r'(\d+) ', raw_name)
            return int(is_bottles_pack.group(1)) if is_bottles_pack is not None else 1

        # "6 Bottles Pack"
        is_pack = re.search(r'(\d+) Pack', raw_name)
        if is_pack:
            return int(is_pack.group(1))

        # "La Chouffe Belgian Strong Golden Ale, 4x330ml"
        is_ml = re.search(r'(\d+)x\d{3}ml', raw_name, flags=re.IGNORECASE)
        if is_ml:
            return int(is_ml.group(1))

        # "LA TRAPPE TRIPEL BOTTLE 330ML*3"
        is_multiply = re.search(r'\d{3}ml[*](\d+)', raw_name, flags=re.IGNORECASE)
        if is_multiply:
            return int(is_multiply.group(1))

        # "Lion City Meadery Hibiscus Blueberry Mead 330ml x 6"
        is_ml_reverse = re.search(r'\d{3}ml x (\d+)', raw_name, flags=re.IGNORECASE)
        if is_ml_reverse:
            return int(is_ml_reverse.group(1))

        return 1
