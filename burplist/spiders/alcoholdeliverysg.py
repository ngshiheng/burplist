import scrapy
from burplist.items import ProductItem
from scrapy.loader import ItemLoader
from scrapy_splash import SplashRequest


class AlcoholDeliverySGSpider(scrapy.Spider):
    name = 'alcoholdelivery'
    allowed_domains = ['alcoholdelivery.com.sg']
    start_urls = ['https://www.alcoholdelivery.com.sg/beer-cider/craft-beer']

    def start_requests(self):
        # FIXME: Currently Splash is stuck at loading a js popup that requires user to enter their age.
        yield SplashRequest(url=self.start_urls, callback=self.parse, endpoint='render.html')

    def parse(self, response):
        products = response.xpath('')

        for product in products:
            loader = ItemLoader(item=ProductItem(), selector=product)
            loader.add_xpath('name', '')
            loader.add_xpath('price', '')
            loader.add_xpath('url', '')
            yield loader.load_item()
