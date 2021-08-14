import logging
import re

import scrapy
import sentry_sdk
from burplist.items import ProductItem
from scrapy.loader import ItemLoader

logger = logging.getLogger(__name__)


class ThirstySpider(scrapy.Spider):
    """
    Extract data from raw HTML
    Do note that this site uses infinite scrolling

    # TODO: Add contracts to `parse_collection`. Need to handle passing of `meta`
    """
    name = 'thirsty'
    custom_settings = {'ROBOTSTXT_OBEY': False}
    start_urls = ['https://www.thirsty.com.sg/pages/shop-by-style']

    def parse(self, response):
        """
        @url https://www.thirsty.com.sg/pages/shop-by-style
        @returns requests 1
        """
        collections = response.xpath('//a[@class="link-3 color-header"]')

        for collection in collections:
            style = collection.xpath('text()').get()
            yield response.follow(collection, callback=self.parse_collection, meta={'style': style})

    def parse_collection(self, response):
        page = response.meta.get('page', 1)
        current_url = response.request.url if page == 1 else response.meta['current_url']  # So that query parameters wont be appended whenever this method runs recursively

        products = response.xpath('//div[@class="text-left pr-0 col-8 col-tablet-12 tablet-pl-0 tablet-pr-0 col-desktop-12 desktop-pl-0 desktop-pr-0 cf"]')

        # NOTE: Because we don't have a way to determine if this request has next page, we would just stop following when `products` is not found
        if products:
            for product in products:
                url = response.urljoin(product.xpath('.//a[@class="link-3 color-header"]/@href').get())

                raw_prices = product.xpath('.//span[@class="color-header body-s"]/text()').getall()
                display_units = product.xpath('.//p[@class="product-option-title body-xxs ml-5"]/text()').getall()

                if len(raw_prices) != len(display_units):
                    logger.warning('Mismatch length of `raw_prices` and `display_units`.')

                    with sentry_sdk.push_scope() as scope:
                        scope.set_extra('url', url)
                        scope.set_extra('raw_prices', raw_prices)
                        scope.set_extra('display_units', display_units)
                        sentry_sdk.capture_message('Mismatch length of `raw_prices` and `display_units`.', 'warning')
                    continue

                for price, display_unit in zip(raw_prices, display_units):
                    loader = ItemLoader(item=ProductItem(), selector=product)

                    loader.add_value('platform', self.name)

                    loader.add_xpath('name', './/a[@class="link-3 color-header"]/text()')
                    loader.add_value('url', url)

                    loader.add_xpath('brand', './/a[@class="body-xs color-text"]/text()')
                    loader.add_xpath('origin', None)
                    loader.add_value('style', response.meta['style'])

                    loader.add_xpath('abv', './/span[@class="alcohol color-text body-xs mr-5"]/text()')
                    loader.add_xpath('volume', './/span[@class="volume color-text body-xs tablet-mr-5"]/text()')
                    loader.add_value('quantity', self.get_product_quantity(display_unit))

                    loader.add_value('price', price)

                    yield loader.load_item()

            page += 1
            next_page = f'{current_url}?view=json&sort_by=manual&page={page}'
            yield response.follow(next_page, callback=self.parse_collection, meta={'current_url': current_url, 'page': page, 'style': response.meta['style']})

    @staticmethod
    def get_product_quantity(display_unit: str) -> int:
        quantity = re.split('x', display_unit, flags=re.IGNORECASE)  # E.g.: "DisplayUnit": "24 x 330ml". Note that 'x' can be capital letter
        return int(quantity[0]) if len(quantity) != 1 else 1
