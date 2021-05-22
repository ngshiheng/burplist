import logging
import os

import scrapy
from burplist.items import ProductItem
from burplist.utils.parsers import get_product_name_quantity
from scrapy.loader import ItemLoader
from scrapy.utils.project import get_project_settings

logger = logging.getLogger(__name__)

settings = get_project_settings()


class ShopeeSpider(scrapy.Spider):
    """
    Parse data from site's API
    """
    name = 'shopee'
    custom_settings = {
        'DOWNLOAD_DELAY': os.environ.get('SHOPEE_DOWNLOAD_DELAY', 5),
    }

    start_urls = [
        f'https://shopee.sg/api/v4/search/search_items?by=sales&keyword=Beer%20%26%20Cider&limit=50&match_id=14255&newest={n}&order=desc&page_type=search&rating_filter=4&scenario=PAGE_SUB_CATEGORY_SEARCH&skip_autocorrect=1&version=2'
        for n in range(0, 250, 50)
    ]

    def parse(self, response):
        logger.info(response.request.headers)
        data = response.json()

        items = data['items']

        # Stop sending requests when the REST API returns an empty array
        if items:
            for item in items:
                product = item['item_basic']
                item_id = product['itemid']
                shop_id = product['shopid']

                loader = ItemLoader(item=ProductItem(), selector=product)

                name, quantity = get_product_name_quantity(product['name'])

                price = str(product['price'] / 100000)  # Shopee price example: 4349000 = $43.49

                loader.add_value('platform', self.name)
                loader.add_value('name', name)
                loader.add_value('price', price)
                loader.add_value('quantity', quantity)
                loader.add_value('url', f'https://shopee.sg/--i.{shop_id}.{item_id}')
                yield loader.load_item()
