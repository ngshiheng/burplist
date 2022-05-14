from typing import Generator

import scrapy
from burplist.items import ProductLoader
from burplist.locators.hopshop import HopShopLocator
from burplist.utils.parsers import parse_style


class HopShopSpider(scrapy.Spider):
    """Parse data from raw HTML

    Page number based pagination
    All scrapped item from this site are of quantity of 1

    # TODO: Extract `origin` and partially missing `style` information
    """

    name = 'hopshop'
    start_urls = ['https://www.hopshop.com.sg/beer/']

    def parse(self, response) -> Generator[scrapy.Request, None, None]:
        """
        @url https://www.hopshop.com.sg/beer/
        @returns items 1
        @returns requests 1 1
        @scrapes platform name url brand abv volume quantity price
        """
        products = response.xpath(HopShopLocator.products)

        for product in products:
            name = product.xpath(HopShopLocator.product_name).get()
            style = parse_style(product.xpath(HopShopLocator.product_style).get()) or parse_style(name)

            loader = ProductLoader(selector=product)

            loader.add_value('platform', self.name)
            loader.add_value('name', name)
            loader.add_value('url', response.urljoin(product.xpath(HopShopLocator.product_url).get()))

            loader.add_xpath('brand', HopShopLocator.product_brand)
            loader.add_xpath('origin', None)
            loader.add_value('style', style)

            loader.add_value('abv', name)
            loader.add_value('volume', name)
            loader.add_value('quantity', 1)

            loader.add_xpath('image_url', HopShopLocator.product_image_url)

            loader.add_xpath('price', HopShopLocator.product_price)
            yield loader.load_item()

        # Recursively follow the link to the next page, extracting data from it
        has_next_page = response.xpath(HopShopLocator.next_page).get()
        if has_next_page is not None:
            next_page = response.urljoin(has_next_page)
            yield response.follow(next_page, callback=self.parse)
