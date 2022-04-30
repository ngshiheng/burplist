import scrapy

from burplist.items import ProductLoader
from burplist.locators.giant import GiantLocator
from burplist.utils.parsers import parse_style, parse_volume


class GiantSpider(scrapy.Spider):
    """Parse data from raw HTML"""

    name = 'giant'
    start_urls = ['https://giant.sg/beers-wines-spirits/beers-ciders']

    def parse(self, response):
        """
        @url https://giant.sg/beers-wines-spirits/beers-ciders
        @returns items 1
        @returns requests 1 1
        @scrapes platform name url brand quantity image_url price
        """
        products = response.xpath(GiantLocator.products)

        for product in products:
            loader = ProductLoader(selector=product)

            name = product.xpath(GiantLocator.product_name).get()
            url = product.xpath(GiantLocator.product_url).get()
            brand = product.xpath(GiantLocator.product_brand).get()

            loader.add_value('platform', self.name)
            loader.add_value('name', name)
            loader.add_value('url', f"https://giant.sg/{url}")

            loader.add_value('brand', brand.title())
            loader.add_value('style', parse_style(name))
            loader.add_value('origin', None)

            loader.add_value('abv', None)
            loader.add_value('volume', None)
            loader.add_value('quantity', 1)

            loader.add_xpath('image_url', GiantLocator.product_image_url)

            loader.add_xpath('price', GiantLocator.product_price)
            yield loader.load_item()

        has_next_page = response.xpath(GiantLocator.next_page).get()
        if has_next_page is not None:
            next_page = response.urljoin(has_next_page)
            yield response.follow(next_page, callback=self.parse)
