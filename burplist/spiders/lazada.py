import logging
import os
from urllib.parse import urlencode

import scrapy
from burplist.items import ProductItem
from burplist.utils.extractor import get_product_name_quantity
from burplist.utils.proxy import get_proxy_url
from scrapy.downloadermiddlewares.retry import get_retry_request
from scrapy.loader import ItemLoader
from scrapy.utils.project import get_project_settings

logger = logging.getLogger(__name__)

settings = get_project_settings()


class LazadaSpider(scrapy.Spider):
    """
    Parse data from site's API
    We need to use rotating proxy to scrape from Lazada
    The API structure is similar to Red Mart except that it does not have 'packageInfo'

    Set 'ROBOTSTXT_OBEY': False if you want to use Scrapy API proxy

    Additional product information:
    - Stock Availability
    - Style (name)
    - Volume (name)
    - ABV (name)
    """
    name = 'lazada'
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': os.environ.get('LAZADA_DOWNLOAD_DELAY', 60),
        'DOWNLOADER_MIDDLEWARES': {
            **settings.get('DOWNLOADER_MIDDLEWARES'),
            'burplist.middlewares.DelayedRequestsMiddleware': 100,
        },
    }

    BASE_URL = 'https://www.lazada.sg/shop-beer/?'

    params = {
        'ajax': 'true',
        'rating': 4,  # We filter products that have at least 4 stars and above
        'page': 1,
    }

    def start_requests(self):
        url = self.BASE_URL + urlencode(self.params)
        yield scrapy.Request(url=get_proxy_url(url), callback=self.parse)

    def parse(self, response):
        logger.info(response.request.headers)
        data = response.json()
        if 'rgv587_flag' in data:
            error = f'Rate limited by Lazada. URL <{response.request.url}>.'

            retry_request = get_retry_request(response.request, reason=error, spider=self)
            if retry_request:
                yield retry_request
            return

        products = data['mods']['listItems']

        # Stop sending requests when the REST API returns an empty array
        if products:
            for product in products:
                loader = ItemLoader(item=ProductItem(), selector=product)

                name, quantity = get_product_name_quantity(product['name'])

                loader.add_value('platform', self.name)
                loader.add_value('name', name)
                loader.add_value('price', product['price'])
                loader.add_value('quantity', quantity)
                loader.add_value('url', 'https:' + product['productUrl'])
                yield loader.load_item()

            self.params['page'] += 1
            if int(data['mainInfo']['page']) < 5:  # We only scrape up to 5 pages for Lazada. Anything beyond that are mostly trash
                next_page = self.BASE_URL + urlencode(self.params)
                yield response.follow(get_proxy_url(next_page), callback=self.parse)
