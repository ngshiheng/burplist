from urllib.parse import urlencode

import scrapy
from burplist.items import ProductItem
from scrapy.loader import ItemLoader


class AlcoholDeliverySpider(scrapy.Spider):
    """
    Parse data from site's API
    Site has 'Age Verification' modal
    """
    name = 'alcoholdelivery'
    BASE_URL = 'https://www.alcoholdelivery.com.sg/api/fetchProducts?'

    params = {
        'filter': 'all',
        'keyword': '',
        'limit': 10,
        'parent': 'beer-cider',
        'productList': 1,
        'skip': 0,  # Starting page
        'subParent': 'craft-beer',
        'type': 0,
    }

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Connection': 'keep-alive',
        'Host': 'www.alcoholdelivery.com.sg',
        'Referer': 'https://www.alcoholdelivery.com.sg/beer-cider/craft-beer',
        'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
    }

    def start_requests(self):
        url = self.BASE_URL + urlencode(self.params)
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        products = response.json()

        # Stop sending requests when the REST API returns an empty array
        if products:
            for product in products:
                loader = ItemLoader(item=ProductItem(), selector=product)
                slug = product['slug']

                loader.add_value('name', product['name'])
                loader.add_value('price', str(product['price'] + product['regular_express_delivery']['value']))
                loader.add_value('url', f'https://www.alcoholdelivery.com.sg/product/{slug}')
                yield loader.load_item()

            self.params['skip'] += 10
            next_page = self.BASE_URL + urlencode(self.params)
            yield response.follow(next_page, callback=self.parse)
