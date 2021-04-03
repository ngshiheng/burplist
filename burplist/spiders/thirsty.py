from urllib.parse import urlencode

import scrapy
from burplist.items import ProductItem
from scrapy.loader import ItemLoader


class ColdStorageSpider(scrapy.Spider):
    """
    Parse data from site's API
    """
    name = 'thirsty'
    BASE_URL = 'https://www.thirsty.com.sg/collections/beer?'

    params = {
        'view': 'json',
        'sort_by': 'manual',
        'page': 1,  # Startin page
    }

    def start_requests(self):
        url = self.BASE_URL + urlencode(self.params)
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        products = response.xpath('//div[@class="text-left pr-0 col-8 col-tablet-12 tablet-pl-0 tablet-pr-0 col-desktop-12 desktop-pl-0 desktop-pr-0 cf"]')

        # NOTE: Because we don't have a way to determine if this request has next page, we would just stop following when `products` is not found
        if products:
            for product in products:
                loader = ItemLoader(item=ProductItem(), selector=product)
                loader.add_xpath('name', './/a[@class="link-3 color-header"]/text()')
                loader.add_xpath('price', './/span[@class="color-header body-s"]/text()')  # Returns a list of prices i.e. Single, 6 Packs, Case. `ProductItem` here is set to `TakeFirst`
                loader.add_value('url', response.urljoin(product.xpath('.//a[@class="link-3 color-header"]/@href').get()))
                yield loader.load_item()

            self.params['page'] += 1
            next_page = self.BASE_URL + urlencode(self.params)
            yield response.follow(next_page, callback=self.parse)
