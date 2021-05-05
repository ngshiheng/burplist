import logging
from urllib.parse import urlencode

import scrapy
from burplist.items import ProductItem
from burplist.utils.proxy import get_proxy_url
from scrapy.loader import ItemLoader

logger = logging.getLogger(__name__)


class LazadaSpider(scrapy.Spider):
    """
    Parse data from site's API
    We need to use rotating proxy to scrape from Lazada
    """
    name = 'lazada'
    custom_settings = {'ROBOTSTXT_OBEY': False}
    BASE_URL = 'https://www.lazada.sg/shop-beer/?'

    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json; charset=utf-8',
        'cookie': 'lzd_cid=a3758679-71e7-4bd8-83d7-e962d3061c4a; t_uid=a3758679-71e7-4bd8-83d7-e962d3061c4a; anon_uid=1c7555e3e902081c1242e85a63bb0e56; t_fv=1609208637256; _bl_uid=d8kF2jd1q5Ut2vgtq0F2dqI94htq; fbm_273149279545058=base_domain=.lazada.sg; hng=SG|en-SG|SGD|702; userLanguageML=en; age_limit=18Y; lzd_sid=1d3e9e50807dccb3033f629db42b0c96; _tb_token_=34676e70b566; _m_h5_tk=b2796ef6194f84981bf5eed8ab36866e_1619941814053; _m_h5_tk_enc=d44809b931de9214c3a796a8b69bc8f6; age_restriction=over%3B18%3B1; EGG_SESS=S_Gs1wHo9OvRHCMp98md7KV-HEkamcpqQ-Vq2yGgIUnE_WNwqs4mu-rtADHFezacyJltizHgMYraxBJxxJ87lay9vP4QvjvUJ-yzCg8u3pVo-2iIu_0KI7_a3tCZKrGH8zK88_OxfJF81aWpZhAoAzuSrF6ech38w62KLagiSUQ=; JSESSIONID=CFC48C49433C42AF444FEA50E307CFBC; t_sid=XpS5VeBAEyfxRqthkOm9SQ6jrwbvcsuH; utm_channel=NA; x5sec=7b22617365727665722d6c617a6164613b32223a226237653233396364356466373465616232383731346665653365653330633836434e6941796f5147454e506f6a4f767572654438335145777765576e35506a2f2f2f2f2f41513d3d227d',
    }

    params = {
        'ajax': 'true',
        'rating': 4,  # We filter products that have at least 4 stars and above
        'page': 1,
    }

    retries = 0

    def start_requests(self):
        url = self.BASE_URL + urlencode(self.params)
        yield scrapy.Request(url=get_proxy_url(url), callback=self.parse, headers=self.headers)

    def parse(self, response):
        data = response.json()

        try:
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
                if int(data['mainInfo']['page']) <= int(data['mainInfo']['pageSize']):
                    next_page = self.BASE_URL + urlencode(self.params)
                    yield response.follow(get_proxy_url(next_page), callback=self.parse)

        except KeyError as error:
            logger.warning('Potentially rate limited or blocked by Lazada.')

        except Exception as error:
            logger.exception(error, extra=dict(base_url=self.BASE_URL, headers=self.headers, params=self.params))
