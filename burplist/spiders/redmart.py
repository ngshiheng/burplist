import logging
import os
from urllib.parse import urlencode

import scrapy
from burplist.items import ProductItem
from burplist.spiders.lazada import get_product_name_quantity
from burplist.utils.proxy import get_proxy_url
from scrapy.loader import ItemLoader

logger = logging.getLogger(__name__)


class RedMartSpider(scrapy.Spider):
    """
    Parse data from site's API
    We need to use rotating proxy to scrape from Red Mart
    The API structure is similar to Lazada
    """
    name = 'redmart'
    custom_settings = {'ROBOTSTXT_OBEY': False, 'DOWNLOAD_DELAY': os.environ.get('REDMART_DOWNLOAD_DELAY', 60)}
    # BASE_URL = 'https://redmart.lazada.sg/shop-groceries-winesbeersspirits-beer-craftspecialtybeer/?'
    BASE_URL = 'https://redmart.lazada.sg/shop-beer/?'

    params = {
        'ajax': 'true',
        'from': 'rm_nav_cate',
        'm': 'redmart',
        'rating': 4,  # We filter products that have at least 4 stars and above
        'page': 1,
    }

    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': '-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
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
            if int(data['mainInfo']['page']) < 5:  # We only scrape up to 5 pages for Red Mart. Anything beyond that are mostly trash
                next_page = self.BASE_URL + urlencode(self.params)
                yield response.follow(get_proxy_url(next_page), callback=self.parse, headers=self.headers)
