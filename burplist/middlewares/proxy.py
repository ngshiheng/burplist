import logging
from typing import Optional

from scrapy import Request, Spider
from w3lib.http import basic_auth_header

logger = logging.getLogger(__name__)


class ProxyMiddleware:
    """Middleware to retry requests with proxy

    Reference:
        https://www.zyte.com/blog/scrapy-proxy/
    """

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def __init__(self, settings):
        self.scraperapi_url = 'http://proxy-server.scraperapi.com:8001'
        self.scraperapi_username = 'scraperapi'
        self.scraperapi_api_key = settings.get('SCRAPER_API_KEY')

    @staticmethod
    def check_api_key(api_key: Optional[str]) -> bool:
        if not api_key:
            logger.warning('Proxy API key not set.')
            return False

        return True

    @staticmethod
    def add_proxy(request: Request, proxy_host: str, username: str, api_key: str) -> None:
        request.meta['proxy'] = proxy_host
        request.headers['Proxy-Authorization'] = basic_auth_header(username, api_key)

    def process_request(self, request: Request, spider: Spider) -> None:
        del spider  # Unused

        scraperapi_api_key = self.scraperapi_api_key
        scraperapi_username = self.scraperapi_username
        scraperapi_url = self.scraperapi_url

        retries = request.meta.get('retry_times', 0)

        if retries == 0:
            return

        if self.check_api_key(scraperapi_api_key):
            self.add_proxy(request, scraperapi_url, scraperapi_username, scraperapi_api_key)
            return
