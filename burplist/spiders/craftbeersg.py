import scrapy
from burplist.items import ProductItem
from scrapy.loader import ItemLoader


class CraftbeersgSpider(scrapy.Spider):
    name = 'craftbeersg'
    allowed_domains = ['craftbeersg.com']
    start_urls = ['https://craftbeersg.com/product-category/beer']

    def parse(self, response):
        products = response.xpath('//div[@class="product-inner"]')

        for product in products:
            loader = ItemLoader(item=ProductItem(), selector=product)
            loader.add_xpath('name', './a[@class="product-loop-title"]/h3/text()')
            loader.add_xpath('price', './span[@class="price"]/span/text()')
            loader.add_xpath('url', './a[@class="product-loop-title"]/@href')
            yield loader.load_item()

        # Recursively follow the link to the next page, extracting data from it
        next_page = response.css('a.next.page-numbers').attrib['href']
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
