import scrapy
from burplist.items import ProductItem
from scrapy.loader import ItemLoader


class FairPriceSpider(scrapy.Spider):
    name = 'fairprice'
    allowed_domains = ['fairprice.com']
    start_urls = ['https://www.fairprice.com.sg/category/premium']

    def parse(self, response):
        products = response.xpath('//a[@class="sc-1plwklf-3 bmUXOR"]')

        for product in products:
            loader = ItemLoader(item=ProductItem(), selector=product)
            loader.add_xpath('name', './div/div[@class="sc-1plwklf-8 jQmMcy"]/div[@class="sc-1plwklf-7 jibnUN"]/span/text()')
            loader.add_xpath('price', './div/div[@class="sc-1plwklf-8 jQmMcy"]/div/div/span/span/text()')
            loader.add_value('url', response.urljoin(product.xpath('./@href').get()))
            yield loader.load_item()

        # Coldstorage uses infinite scrolling pagination
