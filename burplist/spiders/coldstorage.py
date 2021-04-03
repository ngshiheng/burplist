import scrapy
from burplist.items import ProductItem
from scrapy.loader import ItemLoader


class ColdStorageSpider(scrapy.Spider):
    """
    Extract data from raw HTML
    Currently `coldstorage` only has a single page data. As `coldstorage` uses infinite scrolling, we need to implement that eventually
    FIXME: Scrape data from different page, handle case where the unit are 4s, 6s etc.
    """
    name = 'coldstorage'
    start_urls = ['https://coldstorage.com.sg/beers-wines-spirits/beer-cider/craft-beers']

    def parse(self, response):
        products = response.xpath('//div[@class="product_box"]')

        for product in products:
            loader = ItemLoader(item=ProductItem(), selector=product)
            loader.add_xpath('name', './a/div[@class="product_detail"]/div[@class="product_category_name"]/div[@class="product_name "]/text()')
            loader.add_xpath('price', './a/div[@class="product_detail"]/div[@class="product_price"]/div/div/text()')
            loader.add_value('url', response.urljoin(product.xpath('./a/@href').get()))
            yield loader.load_item()
