import logging
from urllib.parse import urlencode

import scrapy
from burplist.items import ProductItem
from burplist.utils.parsers import parse_quantity
from scrapy.downloadermiddlewares.retry import get_retry_request
from scrapy.loader import ItemLoader
from scrapy.utils.project import get_project_settings

logger = logging.getLogger(__name__)

settings = get_project_settings()

mainstream_beer_brands = ['tiger', 'asahi', 'carlsberg', 'guinness', 'heineken', 'kronenbourg', 'somersby']


class RedMartSpider(scrapy.Spider):
    """
    Whenever HTTPCACHE_ENABLED is True, retry requests doesn't seem to work well
    I have a feeling that is because referer is being set with cached which Lazada endpoints don't seem to like it

    # TODO: Extract `abv` and `origin` data
    """
    name = 'redmart'
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            **settings.get('DOWNLOADER_MIDDLEWARES'),
            'burplist.middlewares.DelayedRequestsMiddleware': 100,
        },
        'HTTPCACHE_ENABLED': False,
    }

    start_urls = ['https://redmart.lazada.sg/shop-groceries-winesbeersspirits-beer-craftspecialtybeer/?ajax=true']

    def parse(self, response):
        data = response.json()
        if 'rgv587_flag' in data:
            error = f'Rate limited by Red Mart. URL <{response.request.url}>.'

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

            url = 'https://redmart.lazada.sg/shop-groceries-winesbeersspirits-beer-craftspecialtybeer/?' + urlencode(params)
            yield response.follow(url, callback=self.parse_collection, meta={'style': style['title']})

    def parse_collection(self, response):
        data = response.json()
        if 'rgv587_flag' in data:
            error = f'Rate limited by Red Mart. URL <{response.request.url}>.'

            retry_request = get_retry_request(response.request, reason=error, spider=self)
            if retry_request:
                yield retry_request
            return

        products = data['mods'].get('listItems')

        # Stop sending requests when the REST API returns an empty array
        if products:
            for product in products:
                if int(product.get('review', 0)) < 5 or product['brandName'].lower() in mainstream_beer_brands:
                    continue

                item_id = product['itemId']
                shop_id = product['sellerId']

                loader = ItemLoader(item=ProductItem())

                loader.add_value('platform', self.name)

                loader.add_value('name', product['name'])
                loader.add_value('url', f'https://www.lazada.sg/products/-i{item_id}-s{shop_id}.html')  # We could also use `productUrl` here

                loader.add_value('brand', product['brandName'])
                loader.add_value('origin', None)
                loader.add_value('style', response.meta['style'])

                loader.add_value('abv', None)
                loader.add_value('volume', product['name'])

                loader.add_value('quantity', parse_quantity(product['name']))

                loader.add_value('price', product['price'])
                yield loader.load_item()
