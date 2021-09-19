import scrapy
from burplist.items import ProductLoader
from burplist.utils.parsers import parse_style


class HopShopSpider(scrapy.Spider):
    """
    Extract data from raw HTML
    Page number based pagination

    # TODO: Extract `origin` and partially missing `style` information
    """
    name = 'hopshop'
    start_urls = ['https://www.hopshop.com.sg/beer/']

    def parse(self, response):
        """
        @url https://www.hopshop.com.sg/beer/
        @returns items 1
        @returns requests 1 1
        @scrapes platform name url brand abv volume quantity price
        """
        products = response.xpath('//li[@class="product"]')

        for product in products:
            loader = ProductLoader(selector=product)

            loader.add_value('platform', self.name)

            loader.add_xpath('name', './/article/@data-name')
            loader.add_value('url', response.urljoin(product.xpath('.//a/@href').get()))

            loader.add_xpath('brand', './/article/@data-product-brand')
            loader.add_xpath('origin', None)

            style = parse_style(product.xpath('.//article/@data-product-category').get()) or parse_style(product.xpath('.//article/@data-name').get())

            loader.add_value('style', style)

            loader.add_xpath('abv', './/article/@data-name')
            loader.add_xpath('volume', './/article/@data-name')
            loader.add_value('quantity', 1)  # NOTE: All scrapped item from this site are of quantity of 1

            image_url = response.xpath('//div[@class="card-img-container"]//img/@data-src').get()
            loader.add_value('image_url', image_url)

            loader.add_xpath('price', './/article/@data-product-price')
            yield loader.load_item()

        # Recursively follow the link to the next page, extracting data from it
        has_next_page = response.xpath('//li[@class="pagination-item pagination-item--next"]').get()
        if has_next_page is not None:
            next_page = response.urljoin(response.xpath('//li[@class="pagination-item pagination-item--next"]/a/@href').get())
            yield response.follow(next_page, callback=self.parse)
