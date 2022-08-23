import logging
import os
from typing import Generator
from urllib.parse import urlencode

import scrapy
from burplist.items import ProductLoader
from burplist.utils.const import MAINSTREAM_BEER_BRANDS
from burplist.utils.parsers import parse_quantity
from burplist.utils.proxy import get_proxy_url
from scrapy.downloadermiddlewares.retry import get_retry_request
from scrapy.utils.project import get_project_settings

logger = logging.getLogger(__name__)

settings = get_project_settings()


class LazadaSpider(scrapy.Spider):
    """Parse data from REST API

    Whenever HTTPCACHE_ENABLED is True, retry requests doesn't seem to work well
    I have a feeling that is because referer is being set with cached which Lazada endpoints don't seem to like it

    # TODO: Extract `abv` and `origin` data
    # TODO: Add contracts to `parse`. Need to handle passing of `custom_settings`. Currently it keeps getting blocked by anti-scrape system
    """

    name = 'lazada'
    custom_settings = {
        'DOWNLOAD_DELAY': os.environ.get('LAZADA_DOWNLOAD_DELAY', 20),
        'DOWNLOADER_MIDDLEWARES': {
            **settings.get('DOWNLOADER_MIDDLEWARES'),
            'burplist.middlewares.DelayedRequestsMiddleware': 100,
        },
    }

    start_urls = [get_proxy_url('https://www.lazada.sg/shop-groceries-winesbeersspirits-beer-craftspecialtybeer/?ajax=true&from=input&q=craft%20beer')]

    def parse(self, response) -> Generator[scrapy.Request, None, None]:
        """
        @url https://www.lazada.sg/shop-groceries-winesbeersspirits-beer-craftspecialtybeer/?ajax=true&from=input&q=craft%20beer
        @returns requests 1
        """
        logger.info(response.request.headers)
        logger.info(response.ip_address)

        data = response.json()
        if 'rgv587_flag' in data:
            error = f'Rate limited by Lazada. URL <{response.request.url}>.'

            retry_request = get_retry_request(response.request, reason=error, spider=self)
            if retry_request:
                yield retry_request
            return

        styles = data['mods']['filter']['filterItems'][6]['options']  # Contains beer styles

        for style in styles:
            params = {
                'rating': 4,
                'ajax': 'true',  # NOTE: Do not use bool
                'ppath': style['value'],
            }

            url = 'https://www.lazada.sg/shop-groceries-winesbeersspirits-beer-craftspecialtybeer/?' + urlencode(params)
            yield response.follow(get_proxy_url(url), callback=self.parse_collection, meta={'style': style['title']})

    def parse_collection(self, response) -> Generator[scrapy.Request, None, None]:
        data = response.json()
        if 'rgv587_flag' in data:
            error = f'Rate limited by Lazada. URL <{response.request.url}>.'

            retry_request = get_retry_request(response.request, reason=error, spider=self)
            if retry_request:
                yield retry_request
            return

        products = data['mods'].get('listItems')

        # Stop sending requests when the REST API returns an empty array
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
                loader.add_value('url', f'https://www.lazada.sg/products/-i{item_id}-s{shop_id}.html')  # We could also use `productUrl` here

                loader.add_value('brand', brand)
                loader.add_value('origin', None)
                loader.add_value('style', response.meta['style'])

                loader.add_value('abv', None)
                loader.add_value('volume', name)
                loader.add_value('quantity', parse_quantity(name))

                loader.add_value('image_url', product.get('image'))

                loader.add_value('price', product['price'])
                yield loader.load_item()
