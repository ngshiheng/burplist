import scrapy
from burplist.items import ProductItem
from burplist.utils.parsers import get_product_name_quantity
from scrapy.loader import ItemLoader


class BrewerkzSpider(scrapy.Spider):
    """
    Extract data from raw HTML

    Additional product information:
    - Stock Availability (inside)
    - Style (name)
    - Volume (name)
    - ABV (inside)
    """
    name = 'brewerkz'
    start_urls = ['https://sale.brewerkz.com/collections/330ml-beer-can']

    def parse(self, response):
        products = response.xpath('//ul[@class="productGrid productGrid--maxCol3"]//li[@class="product"]')

        for product in products:
            loader = ItemLoader(item=ProductItem(), selector=product)

            name = product.xpath('.//h4[@class="card-title"]/a/text()').get()

            loader.add_value('platform', self.name)
            loader.add_value('name', f'Brewerkz {name}')
            loader.add_xpath('price', './/span[@class="price price--withTax price--main"]')
            loader.add_value('quantity', get_product_name_quantity(name)[1])
            loader.add_xpath('url', './/h4[@class="card-title"]/a/@href')
            yield loader.load_item()

        next_page = response.xpath('//li[@class="pagination-item pagination-item--next"]/a/@href').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield response.follow(next_page, callback=self.parse)
