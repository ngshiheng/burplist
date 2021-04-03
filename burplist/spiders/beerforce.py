import scrapy
from burplist.items import ProductItem
from scrapy.loader import ItemLoader


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
            loader = ItemLoader(item=ProductItem(), selector=product)

            name = product.xpath('.//h3[@class="product__title h4"]/text()').get().strip()
            vendor = product.xpath('.//h4[@class="product__vendor h6"]/text()').get().strip()

            loader.add_value('name', f'{vendor} {name}')
            loader.add_xpath('price', './/span[@class="money"]/text()')
            loader.add_value('quantity', 1)  # NOTE: All scrapped item from this site are of quantity of 1
            loader.add_value('url', response.urljoin(media.xpath('./a/@href').get()))
            yield loader.load_item()

        # Recursively follow the link to the next page, extracting data from it
        has_next_page = response.xpath('//span[@class="next"]/a/@href').get()
        if has_next_page is not None:
            next_page = response.urljoin(response.xpath('//span[@class="next"]/a/@href').get())
            yield response.follow(next_page, callback=self.parse_collection)
