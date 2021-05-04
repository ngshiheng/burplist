from urllib.parse import urlencode

import scrapy
from burplist.items import ProductItem
from scrapy.loader import ItemLoader


class LazadaSpider(scrapy.Spider):
    """
    Parse data from site's API
    """
    name = 'lazada'
    BASE_URL = 'https://www.lazada.sg/shop-beer/?'

    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json; charset=utf-8',
        'cookie': 'lzd_cid=a3758679-71e7-4bd8-83d7-e962d3061c4a; t_uid=a3758679-71e7-4bd8-83d7-e962d3061c4a; anon_uid=1c7555e3e902081c1242e85a63bb0e56; t_fv=1609208637256; _bl_uid=d8kF2jd1q5Ut2vgtq0F2dqI94htq; fbm_273149279545058=base_domain=.lazada.sg; hng=SG|en-SG|SGD|702; userLanguageML=en; age_limit=18Y; lzd_sid=1d3e9e50807dccb3033f629db42b0c96; _tb_token_=34676e70b566; _m_h5_tk=b2796ef6194f84981bf5eed8ab36866e_1619941814053; _m_h5_tk_enc=d44809b931de9214c3a796a8b69bc8f6; age_restriction=over%3B18%3B1; EGG_SESS=S_Gs1wHo9OvRHCMp98md7KV-HEkamcpqQ-Vq2yGgIUnE_WNwqs4mu-rtADHFezacyJltizHgMYraxBJxxJ87lay9vP4QvjvUJ-yzCg8u3pVo-2iIu_0KI7_a3tCZKrGH8zK88_OxfJF81aWpZhAoAzuSrF6ech38w62KLagiSUQ=; t_sid=AJjw4nmzv7ZB8cvcEPexYVpJzCwhtvA8; utm_channel=NA; x5sec=7b22617365727665722d6c617a6164613b32223a2265633961666333653963333436666632643431633734613165653666396637664350665178595147454950467559715572737a45626a44423561666b2b502f2f2f2f3842227d; JSESSIONID=D93391112DC75C33BBF46D4EFDA1BA43',
    }

    params = {
        'ajax': 'true',
        'rating': 4,  # We filter products that have at least 4 stars and above
        'page': 1,
    }

    def start_requests(self):
        url = self.BASE_URL + urlencode(self.params)
        yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)

    def parse(self, response):
        data = response.json()
        products = data['mods']['listItems']

        # Stop sending requests when the REST API returns an empty array
        if products:
            for product in products:
                loader = ItemLoader(item=ProductItem(), selector=product)

                # We ignore the product if it has less than 20 reviews
                if int(product['review']) < 20:
                    continue

                loader.add_value('vendor', self.name)
                loader.add_value('name', product['name'])
                loader.add_value('price', product['price'])
                loader.add_value('quantity', 24)
                loader.add_value('url', product['productUrl'].replace('//', ''))
                yield loader.load_item()

            self.params['page'] += 1
            if int(data['mainInfo']['pageSize']) <= 40:
                next_page = self.BASE_URL + urlencode(self.params)
                yield response.follow(next_page, callback=self.parse)
