import logging
import os
from typing import Generator
from urllib.parse import urlencode

import scrapy
from scrapy.utils.project import get_project_settings

from burplist.items import ProductLoader
from burplist.utils.const import MAINSTREAM_BEER_BRANDS
from burplist.utils.parsers import parse_quantity
from burplist.utils.proxy import get_proxy_url

logger = logging.getLogger(__name__)

settings = get_project_settings()


class LazadaSpider(scrapy.Spider):
    """Scrape data from Lazada REST API.

    # TODO: Extract `abv` and `origin` data
    # TODO: Add contracts to `parse`. Need to handle passing of `custom_settings`. Currently it keeps getting blocked by anti-scrape system
    """

    name = 'lazada'
    custom_settings = {
        'DOWNLOAD_DELAY': os.environ.get('LAZADA_DOWNLOAD_DELAY', 5),
        'DOWNLOADER_MIDDLEWARES': {
            **settings.get('DOWNLOADER_MIDDLEWARES'),
            'burplist.middlewares.DelayedRequestsMiddleware': 100,
        },
    }
    base_url = 'https://www.lazada.sg/shop-groceries-winesbeersspirits-beer-craftspecialtybeer'
    start_urls = [get_proxy_url(f'{base_url}/?ajax=true')]

    def parse(self, response) -> Generator[scrapy.Request, None, None]:
        """
        @url https://www.lazada.sg/shop-groceries-winesbeersspirits-beer-craftspecialtybeer/?ajax=true
        @returns requests 1
        """
        data = response.json()
        filter_items = data['mods']['filter']['filterItems'][2]
        if filter_items['title'] != 'Beer Type':
            raise ValueError('Invalid ppath.')

        styles = filter_items['options']
        for style in styles:
            params = {
                'rating': 4,
                'ajax': 'true',
                'ppath': style['value'],
            }

            url = self.base_url + urlencode(params)
            yield response.follow(get_proxy_url(url), callback=self.parse_collection, meta={'style': style['title']})

    def parse_collection(self, response) -> Generator[scrapy.Request, None, None]:
        data = response.json()
        products = data['mods'].get('listItems')

        if products:
            for product in products:
                name = product['name']
                brand = product['brandName'].strip()
                review = int(product.get('review', '0'))

                if review < 5 or (brand.lower() in MAINSTREAM_BEER_BRANDS):
                    logger.info('Skipping item because of low rating or brand.')
                    continue

                item_id = product['itemId']
                shop_id = product['sellerId']

                loader = ProductLoader()

                loader.add_value('platform', self.name)
                loader.add_value('name', name)
                loader.add_value('url', f'https://www.lazada.sg/products/-i{item_id}-s{shop_id}.html')

                loader.add_value('brand', brand)
                loader.add_value('origin', None)
                loader.add_value('style', response.meta['style'])

                loader.add_value('abv', None)
                loader.add_value('volume', name)
                loader.add_value('quantity', parse_quantity(name))

                loader.add_value('image_url', product.get('image'))

                loader.add_value('price', product['price'])
                yield loader.load_item()
