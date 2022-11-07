import os
from typing import Generator

import scrapy

from burplist.items import ProductLoader
from burplist.utils.parsers import parse_brand, parse_quantity, parse_style


class ShopeeSpider(scrapy.Spider):
    """Scrape data from Shopee API

    https://shopee.sg/
    """

    name = 'shopee'
    custom_settings = {
        'DOWNLOAD_DELAY': os.environ.get('SHOPEE_DOWNLOAD_DELAY', 5),
    }

    start_urls = [
        f'https://shopee.sg/api/v4/search/search_items?by=sales&categoryids=100860&keyword=craft%20beer&limit=50&newest={n}&order=desc&page_type=search&rating_filter=4&scenario=PAGE_GLOBAL_SEARCH&version=2'
        for n in range(0, 200, 50)  # Page 1 to 5
    ]

    headers = {
        'af-ac-enc-dat': 'AAcyLjQuMS0yAAABhEL7l5QAAAtFAj4AAAAAAAAAAOYyhFAbVQMMpIKa2+dGIBkKaWUVkWOzjLDykZY2dhCO2aemln1UTUS5+au1jIfY7R1Euk28HZ2GTC6Gy8upKta1AomlahQQzJTI3QAyabrcR+HjRE5RJ4xmgqF0pQNNgJWI5Ixc+XXsPExyZcR6n6fQ8y9qv9e+0i2RFxL9D/LW5RfDxbm3aN4QLhF3xSQUSdhFgxFdjSR7fl8kZiNFp11d12JqI4GTqcIATPt0rYY/lg4GZtDRXf4x2yTcLYISZjjnR9AUjPhml6U83c4YR74/vnZjSA2ERGYorMHDENw4Z9+Tuci8nLq+lJGsF/QQZ4cpeG2ZUbatRPTf42k24UXHBZsicXs8yj3KGje9gM5DBdGp9SC7AzprcJ/dvAMt1ZE2pQeZodbQEboXldfnVQFaMWIRa4PXPgZbPTbQrS6pIpLnj37lZQEr3GBZds8j2v70yZKvj0zWrczR/hh97tTxzycK0Dv39rAuuGC+V6bDol7tQtal5Gv4mni39rtOgLdZw4Hfjpcb9HHvBsWrWyhnyF1hqOdk2mvItkQwyQJac9YQx1Jd3lC+REE4Rd+g0DJE9KlDf2xEAkaDTZA0clzBUpm1uAhv9Tyih0QRRViyudt/vxC3q7r7Amu/FcS/fiwQIrKIho5LxORIkIvYHmXWjcsYEz9S9S9p+tV1HIfZaPBju6lh2dK2YKJ14RudySmaqnWRY7OMsPKRljZ2EI7Zp6aWkWOzjLDykZY2dhCO2aemlszDf5SsFtL4FgoZmajdOR0=',
    }

    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)

    def parse(self, response) -> Generator[scrapy.Request, None, None]:
        """
        @url https://shopee.sg/api/v4/search/search_items?by=sales&categoryids=100860&keyword=craft%20beer&limit=50&newest=50&order=desc&page_type=search&rating_filter=4&scenario=PAGE_GLOBAL_SEARCH&version=2
        @returns items 1
        @returns requests 0 0
        @scrapes platform name url quantity price
        """
        data = response.json()
        items = data['items']

        if items:
            for item in items:
                product = item['item_basic']
                name = product.get('name')
                brand = product.get('brand')

                if brand is None or brand == 'None' or brand == '' or brand == '0':
                    brand = parse_brand(name)

                item_id = str(product['itemid'])
                shop_id = str(product['shopid'])

                loader = ProductLoader()

                loader.add_value('platform', self.name)
                loader.add_value('name', name)
                loader.add_value('url', f'https://shopee.sg/--i.{shop_id}.{item_id}')

                loader.add_value('brand', brand)  # NOTE: Shopee's API product['brand'] does not guarantee that brand is always correct. They could be None, "None" at times
                loader.add_value('origin', None)
                loader.add_value('style', parse_style(name))

                loader.add_value('abv', None)
                loader.add_value('volume', name)
                loader.add_value('quantity', parse_quantity(name))

                image_id = product.get('image')
                loader.add_value('image_url', f'https://cf.shopee.sg/file/{image_id}')

                loader.add_value('price', product['price'] / 100000)  # e.g. '4349000' = '$43.49'
                yield loader.load_item()
