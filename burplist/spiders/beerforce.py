import logging

import scrapy
from burplist.items import ProductItem
from scrapy.loader import ItemLoader

logger = logging.getLogger(__name__)


class BeerForceSpider(scrapy.Spider):
    """
    Extract data from raw HTML
    Starting URL is from a base URL which contains different styles of beer
    Expect all of the product listed here are either in 'Single' quantity
    """
    name = 'beerforce'
    start_urls = ['https://beerforce.sg/pages/all-styles']

    def parse(self, response):
        collections = response.xpath('//div[@class="o-layout__item u-1/2@tab u-1/4@desk"]')

        for collection in collections:
            url = response.urljoin(collection.xpath('./a/@href').get())
            yield scrapy.Request(url=url, callback=self.parse_collection)

    def parse_collection(self, response):
        product_details = response.xpath('//div[@class="product__details"]')
        product_media = response.xpath('//div[@class="product-top"]')

        for product, media in zip(product_details, product_media):
            raw_price = product.xpath('.//span[@class="money"]/text()').get()

            if raw_price is None:
                logger.info('Skipping item because it is sold out.')
                continue

            loader = ItemLoader(item=ProductItem(), selector=product)
            loader.add_value('platform', self.name)

            loader.add_xpath('name', './/h3[@class="product__title h4"]/text()')
            loader.add_value('url', response.urljoin(media.xpath('./a/@href').get()))

            loader.add_xpath('brand', './/h4[@class="product__vendor h6"]/text()')

            loader.add_value('quantity', 1)  # NOTE: All scrapped item from this site are of quantity of 1

            loader.add_xpath('price', './/span[@class="money"]/text()')

            yield scrapy.Request(
                response.urljoin(media.xpath('./a/@href').get()),
                callback=self.parse_product_detail,
                meta={'item': loader.load_item()},
                dont_filter=False
            )

        # Recursively follow the link to the next page, extracting data from it
        has_next_page = response.xpath('//span[@class="next"]/a/@href').get()
        if has_next_page is not None:
            next_page = response.urljoin(response.xpath('//span[@class="next"]/a/@href').get())
            yield response.follow(next_page, callback=self.parse_collection)

    def parse_product_detail(self, response):
        loadernext = ItemLoader(item=response.meta['item'], response=response)

        product_info = ''.join(response.xpath('//div[@class="product-single__content-text rte"]/p/*/text()').getall())
        style, volume, abv = product_info.split('|', maxsplit=2)
        loadernext.add_value('origin', None)
        loadernext.add_value('style', style)

        loadernext.add_value('abv', abv)
        loadernext.add_value('volume', volume)

        yield loadernext.load_item()
