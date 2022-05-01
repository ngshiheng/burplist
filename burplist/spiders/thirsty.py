import logging
import re

import scrapy
import sentry_sdk
from burplist.items import ProductLoader
from burplist.locators.thirsty import ThirstyLocator

logger = logging.getLogger(__name__)


class ThirstySpider(scrapy.Spider):
    """Parse data from raw HTML

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
        collections = response.xpath(ThirstyLocator.beer_collection)

        for collection in collections:
            style = collection.xpath('text()').get()
            yield response.follow(collection, callback=self.parse_collection, meta={'style': style})

    def parse_collection(self, response):
        page = response.meta.get('page', 1)
        current_url = response.request.url if page == 1 else response.meta['current_url']  # So that query parameters wont be appended whenever this method runs recursively

        products = response.xpath(ThirstyLocator.products)

        # Because we don't have a way to determine if this request has next page, we would just stop following when `products` is not found
        if products:
            for product in products:
                url = response.urljoin(product.xpath(ThirstyLocator.product_title).get())

                raw_prices = product.xpath(ThirstyLocator.product_prices).getall()
                display_units = product.xpath(ThirstyLocator.product_display_units).getall()

                if len(raw_prices) != len(display_units):
                    logger.warning('Mismatch length of `raw_prices` and `display_units`.')

                    with sentry_sdk.push_scope() as scope:
                        scope.set_extra('url', url)
                        scope.set_extra('raw_prices', raw_prices)
                        scope.set_extra('display_units', display_units)
                        sentry_sdk.capture_message('Mismatch length of `raw_prices` and `display_units`.', 'warning')
                    continue

                for price, display_unit in zip(raw_prices, display_units):
                    loader = ProductLoader(selector=product)

                    loader.add_value('platform', self.name)
                    loader.add_xpath('name', ThirstyLocator.product_name)
                    loader.add_value('url', url)

                    loader.add_xpath('brand', ThirstyLocator.product_brand)
                    loader.add_xpath('origin', None)
                    loader.add_value('style', response.meta['style'])

                    loader.add_xpath('abv', ThirstyLocator.product_abv)
                    loader.add_xpath('volume', ThirstyLocator.product_volume)
                    loader.add_value('quantity', self.get_product_quantity(display_unit))

                    image_url = product.xpath(ThirstyLocator.product_image_url).get()
                    loader.add_value('image_url', f'https:{image_url}')

                    loader.add_value('price', price)

                    yield loader.load_item()

            page += 1
            next_page = f'{current_url}?view=json&sort_by=manual&page={page}'
            yield response.follow(next_page, callback=self.parse_collection, meta={'current_url': current_url, 'page': page, 'style': response.meta['style']})

    @staticmethod
    def get_product_quantity(display_unit: str) -> int:
        quantity = re.split('x', display_unit, flags=re.IGNORECASE)  # "24 x 330ml". "x" could be upper case
        return int(quantity[0]) if len(quantity) != 1 else 1
