import re
from typing import Any, Generator
from urllib.parse import urlencode

import scrapy

from burplist.items import ProductLoader
from burplist.utils.parsers import parse_style


class FairPriceSpider(scrapy.Spider):
    """Scrape data from NTUC FairPrice API

    https://www.fairprice.com.sg/category/craft-beer
    """

    name = 'fairprice'
    base_url = 'https://website-api.omni.fairprice.com.sg/api/product/v2?'

    params: dict[str, Any] = {
        'category': 'craft-beer',
        'experiments': 'recHome-B%2CbsHome-B%2CpastPurchaseCategory-B%2CsearchVariant-B%2CtrendH-B%2CtimerVariant-Z%2CinlineBanner-A%2Csp-B%2CsubstitutionBSVariant-A%2Cgv-A%2CSPI-Z%2CSNLI-A%2CSC-A%2CSellerCrtVariant-B%2Cdc-expB%2CadLabel-A%2CsubstitutionVariant-B%2CsubstitutionVariant-B%2CsubstitutionVariant-B%2CsubstitutionVariant-B%2CsubstitutionVariant-B%2CsubstitutionVariant-B%2CsubstitutionVariant-B%2CsubstitutionVariant-B',
        'includeTagDetails': 'true',
        'page': 1,  # Starting page
        'pageType': 'category',
        'slug': 'craft-beer',
        'storeId': '165',
        'url': 'craft-beer',
    }

    headers = {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en',
        'Content-Type': 'application/json',
        'Host': 'website-api.omni.fairprice.com.sg',
        'Origin': 'https///www.fairprice.com.sg',
        'Referer': 'https//www.fairprice.com.sg/',
    }

    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        url = self.base_url + urlencode(self.params)
        yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)

    def parse(self, response) -> Generator[scrapy.Request, None, None]:
        """
        @url https://website-api.omni.fairprice.com.sg/api/product/v2?category=craft-beer&experiments=recHome-B%252CbsHome-B%252CpastPurchaseCategory-B%252CsearchVariant-B%252CtrendH-B%252CtimerVariant-Z%252CinlineBanner-A%252Csp-B%252CsubstitutionBSVariant-A%252Cgv-A%252CSPI-Z%252CSNLI-A%252CSC-A%252CSellerCrtVariant-B%252Cdc-expB%252CadLabel-A%252CsubstitutionVariant-B%252CsubstitutionVariant-B%252CsubstitutionVariant-B%252CsubstitutionVariant-B%252CsubstitutionVariant-B%252CsubstitutionVariant-B%252CsubstitutionVariant-B%252CsubstitutionVariant-B&includeTagDetails=true&page=1&pageType=category&slug=craft-beer&storeId=165&url=craft-beer
        @returns items 1
        @returns requests 1
        @scrapes platform name url brand origin quantity price
        """
        data = response.json()['data']
        products = data['product']

        if products:
            for product in products:
                name = product['name']
                brand = product['brand']['name']
                metadata = product['metaData']
                slug = product['slug']

                loader = ProductLoader()

                loader.add_value('platform', self.name)
                loader.add_value('name', name)
                loader.add_value('url', f'https://www.fairprice.com.sg/product/{slug}')

                loader.add_value('brand', brand)
                loader.add_value('origin', metadata['Country of Origin'])
                loader.add_value('style', parse_style(metadata.get('Key Information', '')))

                loader.add_value('abv', name)
                loader.add_value('volume', metadata['DisplayUnit'])
                loader.add_value('quantity', self.get_product_quantity(product))

                image_url = product['images'][0]
                loader.add_value('image_url', image_url)

                loader.add_value('price', self.get_product_price(product))

                yield loader.load_item()

            has_next_page = data['pagination']['page'] < data['pagination']['total_pages']
            if has_next_page is True:
                self.params['page'] += 1
                next_page = self.base_url + urlencode(self.params)
                yield response.follow(next_page, callback=self.parse)

    @ staticmethod
    def get_product_price(product: dict[str, Any]) -> Any:
        offer = product.get('offers')
        if offer and offer[0]['price'] is not None:
            return offer[0]['price']

        return product['storeSpecificData'][0]['mrp']

    @ staticmethod
    def get_product_quantity(product: dict[str, Any]) -> int:
        metadata = product['metaData']
        display_unit = metadata['DisplayUnit']
        quantity = re.split('x', display_unit, flags=re.IGNORECASE)  # "24 x 330ml". "x" could be upper case

        return int(quantity[0]) if len(quantity) != 1 else 1
