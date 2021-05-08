import scrapy
from burplist.items import ProductItem
from scrapy.loader import ItemLoader


class HopShopSpider(scrapy.Spider):
    """
    Extract data from raw HTML
    Page number based pagination

    Additional product information:
    - Stock Availability (inside, exact amount)
    - Style (name)
    - Volume (name)
    - ABV (name)
    """
    name = 'hopshop'
    start_urls = ['https://www.hopshop.com.sg/beer/']

    def parse(self, response):
        products = response.xpath('//li[@class="product"]')

        for product in products:
            loader = ItemLoader(item=ProductItem(), selector=product)

            loader.add_value('vendor', self.name)
            loader.add_xpath('name', './/article/@data-name')
            loader.add_xpath('price', './/article/@data-product-price')
            loader.add_value('quantity', 1)  # NOTE: All scrapped item from this site are of quantity of 1
            loader.add_value('url', response.urljoin(product.xpath('.//a/@href').get()))
            yield loader.load_item()

        # Recursively follow the link to the next page, extracting data from it
        has_next_page = response.xpath('//li[@class="pagination-item pagination-item--next"]').get()
        if has_next_page is not None:
            next_page = response.urljoin(response.xpath('//li[@class="pagination-item pagination-item--next"]/a/@href').get())
            yield response.follow(next_page, callback=self.parse)
