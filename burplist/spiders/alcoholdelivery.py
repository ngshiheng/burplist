from urllib.parse import urlencode

import scrapy
from burplist.items import ProductItem
from scrapy.loader import ItemLoader


class AlcoholDeliverySpider(scrapy.Spider):
    """
    Parse data from site's API
    Site has 'Age Verification' modal
    Expect all of the product listed here are either in 'Single' or 'Keg'
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
        'subParent': '',  # set as 'craft-beer' to only get craft beer data
        'type': 0,
    }

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Connection': 'keep-alive',
        'Cookie': 'deliverykey=60557e3de9fd6ef8108b4568; ageverfication=%7B%22month%22%3A2%2C%22day%22%3A6%2C%22year%22%3A1993%7D; XSRF-TOKEN=eyJpdiI6IkZFejlrNG9pKzJ4XC9Vb3JHa3RDWnJBPT0iLCJ2YWx1ZSI6Im1JVmNxb2VBMksyNThtS3dCRFQ2aFo1UEZra0F6XC9kRWJLZkNGc3d1Y0wxclNvUkVqd0RDRDRaM0c3Q0pPT3laYjBQcFdnVFFRMU40YzkxTHNzVFwvNmc9PSIsIm1hYyI6IjNlZWY1OTYzNWE2ZTZkZmY2Y2QwZGRiZDdlNDQzODNkY2I4MjRhMWIyNTk5N2NkYzc1MmRlMDFjYzIwYTc0YmUifQ%3D%3D; api_token=eyJpdiI6ImwzNno3YVUya3pSVjRFdnA3eFZ1bkE9PSIsInZhbHVlIjoiMEt3TGR6OE8reDBmQkt3bFdTZzMrWVVpNkN2ZUNMYWtIOFdVUkJreHZ1bTVqOVArS2tcL3dWbmRIS3g1WlBTckMra2tWUWdiMEt2WlYzQWtpU1gyUDRnPT0iLCJtYWMiOiIxOWIyMDcyN2RjMGJmMjIwMDMwMTlhYWIxZDNlNmNjNDE5OGY3NDM1M2YxNTQ1MWU5NzNjMDRkYjg4NTU5ZjJmIn0%3D',
        'Host': 'www.alcoholdelivery.com.sg',
        'Referer': 'https://www.alcoholdelivery.com.sg/beer-cider',
        'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
        'X-XSRF-TOKEN': 'eyJpdiI6IkZFejlrNG9pKzJ4XC9Vb3JHa3RDWnJBPT0iLCJ2YWx1ZSI6Im1JVmNxb2VBMksyNThtS3dCRFQ2aFo1UEZra0F6XC9kRWJLZkNGc3d1Y0wxclNvUkVqd0RDRDRaM0c3Q0pPT3laYjBQcFdnVFFRMU40YzkxTHNzVFwvNmc9PSIsIm1hYyI6IjNlZWY1OTYzNWE2ZTZkZmY2Y2QwZGRiZDdlNDQzODNkY2I4MjRhMWIyNTk5N2NkYzc1MmRlMDFjYzIwYTc0YmUifQ==',
    }

    def start_requests(self):
        url = self.BASE_URL + urlencode(self.params)
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        products = response.json()

        # Stop sending requests when the REST API returns an empty array
        if products:
            for product in products:

                # Filter out product with 'Keg' inside the name
                if any(word in product['name'].lower() for word in ['keg', 'litre']):
                    continue

                loader = ItemLoader(item=ProductItem(), selector=product)
                slug = product['slug']

                loader.add_value('vendor', self.name)
                loader.add_value('name', product['name'])
                loader.add_value('price', str(product['price'] + product['regular_express_delivery']['value']))
                loader.add_value('quantity', 1)  # NOTE: All scrapped item from this site are of quantity of 1
                loader.add_value('url', f'https://www.alcoholdelivery.com.sg/product/{slug}')
                yield loader.load_item()

            self.params['skip'] += 10
            next_page = self.BASE_URL + urlencode(self.params)
            yield response.follow(next_page, callback=self.parse)
