import re
from typing import Any
from urllib.parse import urlencode

import scrapy
from burplist.items import ProductItem
from burplist.utils.parsers import parse_style
from scrapy.loader import ItemLoader


def _get_product_price(product: dict[str, Any]) -> str:
    offer = product.get('offers')

    if offer and offer[0]['price'] is not None:
        return str(offer[0]['price'])

    return product['storeSpecificData'][0]['mrp']


def _get_product_quantity(product: dict[str, Any]) -> int:
    metadata = product['metaData']
    display_unit = metadata['DisplayUnit']
    quantity = re.split('x', display_unit, flags=re.IGNORECASE)  # E.g.: "DisplayUnit": "24 x 330ml". Note that 'x' can be capital letter

    return int(quantity[0]) if len(quantity) != 1 else 1


class FairPriceSpider(scrapy.Spider):
    """
    Parse data from site's API

    # TODO: Extract partially missing `style` information
    """
    name = 'fairprice'
    BASE_URL = 'https://website-api.omni.fairprice.com.sg/api/product/v2?'

    params = {
        'category': 'premium',
        'experiments': 'recHome-A,pastPurchaseCategory-A,searchVariant-B,UnappliedPromoVariant-B,substitutionVariant-B,substitutionVariant-B',
        'includeTagDetails': 'true',
        'page': 1,  # Starting page
        'pageType': 'category',
        'slug': 'premium',
        'storeId': '165',
        'url': 'premium',
    }

    # NOTE: This spider would work without these headers anyway. Adding these in as a safety measure
    headers = {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Host': 'website-api.omni.fairprice.com.sg',
        'Origin': 'https///www.fairprice.com.sg',
        'Referer': 'https//www.fairprice.com.sg/',
        'sec-ch-ua': 'Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99',
        'sec-ch-ua-mobile': '?0',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
    }

    def start_requests(self):
        url = self.BASE_URL + urlencode(self.params)
        yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)

    def parse(self, response):
        """
        @url https://website-api.omni.fairprice.com.sg/api/product/v2?category=premium&experiments=recHome-A%2CpastPurchaseCategory-A%2CsearchVariant-B%2CUnappliedPromoVariant-B%2CsubstitutionVariant-B%2CsubstitutionVariant-B&includeTagDetails=true&page=1&pageType=category&slug=premium&storeId=165&url=premium
        @returns items 20
        @returns requests 1
        @scrapes platform name url brand origin volume quantity price
        """
        data = response.json()['data']
        products = data['product']

        for product in products:
            loader = ItemLoader(item=ProductItem())
            slug = product['slug']

            loader.add_value('platform', self.name)

            loader.add_value('name', product['name'])
            loader.add_value('url', f'https://www.fairprice.com.sg/product/{slug}')

            loader.add_value('brand', product['brand']['name'])
            loader.add_value('origin', product['metaData']['Country of Origin'])
            loader.add_value('style', parse_style(product['metaData'].get('Key Information', '')))

            loader.add_value('abv', product['name'])
            loader.add_value('volume', product['metaData']['DisplayUnit'])
            loader.add_value('quantity', _get_product_quantity(product))

            loader.add_value('price', _get_product_price(product))

            yield loader.load_item()

        has_next_page = data['pagination']['page'] < data['pagination']['total_pages']
        if has_next_page is True:
            self.params['page'] += 1
            next_page = self.BASE_URL + urlencode(self.params)
            yield response.follow(next_page, callback=self.parse)
