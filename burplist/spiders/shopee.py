import logging
import os
from typing import Generator

import scrapy
from burplist.items import ProductLoader
from burplist.utils.const import MAINSTREAM_BEER_BRANDS
from burplist.utils.parsers import parse_brand, parse_quantity, parse_style

logger = logging.getLogger(__name__)


class ShopeeSpider(scrapy.Spider):
    """Parse data from REST API

    # TODO: Extract `origin` and `abv` information
    """

    name = 'shopee'
    custom_settings = {
        'DOWNLOAD_DELAY': os.environ.get('SHOPEE_DOWNLOAD_DELAY', 5),
    }

    start_urls = [
        f'https://shopee.sg/api/v4/search/search_items?by=sales&categoryids=100860&keyword=craft%20beer&limit=50&newest={n}&order=desc&page_type=search&rating_filter=4&scenario=PAGE_GLOBAL_SEARCH&version=2'
        for n in range(0, 200, 50)  # Page 1 to 5
    ]

    def parse(self, response) -> Generator[scrapy.Request, None, None]:
        """
        @url https://shopee.sg/api/v4/search/search_items?by=sales&categoryids=100860&keyword=craft%20beer&limit=50&newest=50&order=desc&page_type=search&rating_filter=4&scenario=PAGE_GLOBAL_SEARCH&version=2
        @returns items 1
        @returns requests 0 0
        @scrapes platform name url quantity price
        """
        data = response.json()
        items = data['items']

        # Stop sending requests when the REST API returns an empty array
        if items:
            for item in items:
                product = item['item_basic']
                name = product.get('name')
                brand = product.get('brand')
                review_count = product['item_rating']['rating_count'][0]

                if brand is None or brand == 'None' or brand == '' or brand == '0':
                    brand = parse_brand(name)

                if review_count < 10 or (brand and brand.lower() in MAINSTREAM_BEER_BRANDS):
                    logger.info('Skipping item because of low rating or brand.')
                    continue

                item_id = str(product['itemid'])
                shop_id = str(product['shopid'])

                loader = ProductLoader()

                loader.add_value('platform', self.name)
                loader.add_value('name', name)
                loader.add_value('url', f'https://shopee.sg/--i.{shop_id}.{item_id}')

                loader.add_value('brand', brand)  # NOTE: Shopee's API product['brand'] does not guarantee that brand is always correct. They could be None, "None" at times
                loader.add_value('origin', None)
                loader.add_value('style', parse_style(name))

                loader.add_value('abv', None)
                loader.add_value('volume', name)
                loader.add_value('quantity', parse_quantity(name))

                image_id = product.get('image')
                loader.add_value('image_url', f'https://cf.shopee.sg/file/{image_id}')

                loader.add_value('price', product['price'] / 100000)  # e.g. '4349000' = '$43.49'
                yield loader.load_item()
