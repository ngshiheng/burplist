import logging

import scrapy
from burplist.items import ProductItem
from burplist.utils.extractor import get_product_name_quantity
from scrapy.downloadermiddlewares.retry import get_retry_request
from scrapy.loader import ItemLoader

logger = logging.getLogger(__name__)


class RedMartSpider(scrapy.Spider):
    """
    Parse data from site's API
    The API structure is similar to Lazada

    - https://redmart.lazada.sg/shop-beer/?from=rm_nav_cate&m=redmart&rating=4
    - https://redmart.lazada.sg/shop-groceries-winesbeersspirits-beer-craftspecialtybeer/?from=rm_nav_cate&m=redmart&rating=4
    """
    name = 'redmart'
    custom_settings = {'DOWNLOAD_DELAY': 20}

    start_urls = [
        f'https://redmart.lazada.sg/shop-groceries-winesbeersspirits-beer-craftspecialtybeer/?ajax=true&from=rm_nav_cate&m=redmart&page={n}&rating=4'
        for n in range(1, 6)
    ] + [
        f'https://redmart.lazada.sg/shop-beer/?ajax=true&from=rm_nav_cate&m=redmart&page={n}&rating=4'
        for n in range(1, 6)
    ]

    def parse(self, response):
        data = response.json()
        if 'rgv587_flag' in data:
            error = f'Rate limited by Red Mart. URL <{response.request.url}>.'
            logger.warning(error)

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

                loader.add_value('vendor', self.name)
                loader.add_value('name', name)
                loader.add_value('price', product['price'])
                loader.add_value('quantity', quantity)
                loader.add_value('url', product['productUrl'].replace('//', ''))
                yield loader.load_item()
