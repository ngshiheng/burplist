from typing import Generator

import scrapy

from burplist.items import ProductLoader
from burplist.locators import BeerForceLocator


class BeerForceSpider(scrapy.Spider):
    """Scrape data from raw HTML

    Starting URL is from a base URL which contains different styles of beer
    Expect all of the product listed here are of 'Single' quantity
    This spider passes ProductLoader item into nested request

    https://beerforce.sg/
    """
    name = 'beerforce'
    start_urls = ['https://beerforce.sg/pages/all-styles']

    def parse(self, response) -> Generator[scrapy.Request, None, None]:
        """
        @url https://beerforce.sg/pages/all-styles
        @returns requests 1
        """
        collections = response.xpath(BeerForceLocator.beer_collection)
        yield from response.follow_all(collections, callback=self.parse_collection)

    def parse_collection(self, response) -> Generator[scrapy.Request, None, None]:
        """
        @url https://beerforce.sg/collections/ipa
        @returns requests 1
        """
        if "/collections/merchandise" in response.request.url:
            return

        product_details = response.xpath(BeerForceLocator.product_details)
        product_media = response.xpath(BeerForceLocator.product_media)

        for product, media in zip(product_details, product_media):
            price = product.xpath(BeerForceLocator.product_price).get()
            if price is None:
                continue

            loader = ProductLoader(selector=product)

            loader.add_value('platform', self.name)
            loader.add_xpath('name', BeerForceLocator.product_name)
            loader.add_value('url', response.urljoin(media.xpath(BeerForceLocator.product_url).get()))

            loader.add_xpath('brand', BeerForceLocator.product_brand)

            loader.add_value('quantity', 1)

            loader.add_value('price', price)

            yield scrapy.Request(
                response.urljoin(media.xpath(BeerForceLocator.product_url).get()),
                callback=self.parse_product_detail,
                meta={'item': loader.load_item()},
                dont_filter=False,
            )

        has_next_page = response.xpath(BeerForceLocator.next_page).get()
        if has_next_page is not None:
            next_page = response.urljoin(has_next_page)
            yield response.follow(next_page, callback=self.parse_collection)

    def parse_product_detail(self, response) -> Generator[scrapy.Request, None, None]:
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
