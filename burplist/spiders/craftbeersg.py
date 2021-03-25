import scrapy


class CraftbeersgSpider(scrapy.Spider):
    name = 'craftbeersg'
    allowed_domains = ['craftbeersg.com']
    start_urls = ['http://craftbeersg.com/']

    def parse(self, response):
        pass
