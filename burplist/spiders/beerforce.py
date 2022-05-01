import logging

import scrapy
from burplist.items import ProductLoader
from burplist.locators.beerforce import BeerForceLocator

logger = logging.getLogger(__name__)


class BeerForceSpider(scrapy.Spider):
    """Parse data from raw HTML

    Starting URL is from a base URL which contains different styles of beer
    Expect all of the product listed here are of 'Single' quantity
    This spider passes ProductItem into nested request

    # TODO: Extract `origin` information
    # TODO: Add contracts to `parse_product_detail`. Need to handle passing of `meta`
    """
    name = 'beerforce'
    start_urls = ['https://beerforce.sg/pages/all-styles']

    def parse(self, response):
        """
        @url https://beerforce.sg/pages/all-styles
        @returns requests 1
        """
        collections = response.xpath(BeerForceLocator.beer_collection)
        yield from response.follow_all(collections, callback=self.parse_collection)

    def parse_collection(self, response):
        """
        @url https://beerforce.sg/collections/ipa
        @returns requests 1
        """
        product_details = response.xpath(BeerForceLocator.product_details)
        product_media = response.xpath(BeerForceLocator.product_media)

        for product, media in zip(product_details, product_media):
            raw_price = product.xpath(BeerForceLocator.raw_price).get()

            if raw_price is None:
                logger.info("Skipping item because it is out of stock.")
                continue

            loader = ProductLoader(selector=product)

            loader.add_value('platform', self.name)
            loader.add_xpath('name', BeerForceLocator.product_name)
            loader.add_value('url', response.urljoin(media.xpath(BeerForceLocator.product_url).get()))

            loader.add_xpath('brand', BeerForceLocator.product_brand)

            loader.add_value('quantity', 1)

            loader.add_xpath('price', BeerForceLocator.product_price)

            yield scrapy.Request(
                response.urljoin(media.xpath(BeerForceLocator.product_url).get()),
                callback=self.parse_product_detail,
                meta={'item': loader.load_item()},
                dont_filter=False,
            )

        # Recursively follow the link to the next page, extracting data from it
        has_next_page = response.xpath(BeerForceLocator.has_next_page).get()
        if has_next_page is not None:
            next_page = response.urljoin(response.xpath(BeerForceLocator.next_page).get())
            yield response.follow(next_page, callback=self.parse_collection)

    def parse_product_detail(self, response):
        loadernext = ProductLoader(item=response.meta['item'], response=response)

        product_info = ''.join(response.xpath(BeerForceLocator.product_info).getall())
        style, volume, abv = product_info.split('|', maxsplit=2)
        loadernext.add_value('origin', None)
        loadernext.add_value('style', style)

        loadernext.add_value('abv', abv)
        loadernext.add_value('volume', volume)

        image_url = response.xpath(BeerForceLocator.product_image_url).get()
        loadernext.add_value('image_url', f'https:{image_url}')

        yield loadernext.load_item()
