import scrapy
from burplist.items import ProductItem
from scrapy.loader import ItemLoader


class ColdStorageSpider(scrapy.Spider):
    name = 'coldstorage'
    allowed_domains = ['coldstorage.com']
    start_urls = ['https://coldstorage.com.sg/beers-wines-spirits/beer-cider/craft-beers']

    def parse(self, response):
        products = response.xpath('//div[@class="product_box"]')

        for product in products:
            loader = ItemLoader(item=ProductItem(), selector=product)
            loader.add_xpath('name', './a/div[@class="product_detail"]/div[@class="product_category_name"]/div[@class="product_name "]/text()')
            loader.add_xpath('price', './a/div[@class="product_detail"]/div[@class="product_price"]/div/div/text()')
            loader.add_value('url', response.urljoin(product.xpath('./a/@href').get()))
            yield loader.load_item()

        # Coldstorage uses infinite scrolling pagination
