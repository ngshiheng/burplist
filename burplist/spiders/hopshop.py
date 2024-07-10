from typing import Generator

import scrapy

from burplist.items import ProductLoader
from burplist.locators import HopShopLocator
from burplist.utils.parsers import parse_style


class HopShopSpider(scrapy.Spider):
    """Scrape data from raw HTML

    Page number based pagination
    All scrapped item from this site are of quantity of 1

    https://www.hopshop.com.sg/beer/
    """

    name = "hopshop"
    start_urls = ["https://www.hopshop.com.sg/beer/"]

    def parse(self, response) -> Generator[scrapy.Request, None, None]:
        collections = response.xpath(HopShopLocator.beer_collection)
        for collection in collections:
            style = collection.xpath("./text()").get().strip()
            yield response.follow(
                collection, callback=self.parse_collection, meta={"style": style}
            )

    def parse_collection(self, response) -> Generator[scrapy.Request, None, None]:
        """
        @url https://www.hopshop.com.sg/ipa/
        """
        products = response.xpath(HopShopLocator.products)
        style = parse_style(response.meta["style"])

        for product in products:
            name = product.xpath(HopShopLocator.product_name).get()
            url = response.urljoin(product.xpath(HopShopLocator.product_url).get())

            loader = ProductLoader(selector=product)

            loader.add_value("platform", self.name)
            loader.add_value("name", name)
            loader.add_value("url", url)

            loader.add_xpath("brand", HopShopLocator.product_brand)
            loader.add_xpath("origin", None)
            loader.add_value("style", style)

            loader.add_value("abv", name)
            loader.add_value("volume", name)
            loader.add_value("quantity", 1)

            loader.add_xpath("image_url", HopShopLocator.product_image_url)

            price = self.get_product_price(
                product.xpath(HopShopLocator.product_price).get()
            )
            loader.add_value("price", price)

            yield loader.load_item()

        has_next_page = response.xpath(HopShopLocator.next_page).get()
        if has_next_page:
            next_page = response.urljoin(has_next_page)
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def get_product_price(raw_price: str) -> str:
        return raw_price.split("-")[0]
