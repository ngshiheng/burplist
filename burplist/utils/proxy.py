import os
import re
from decimal import Decimal
from urllib.parse import urlencode


def get_proxy_url(url: str) -> str:
    """
    We send all our requests to https://www.scraperapi.com/ API endpoint in order use their proxy servers
    This function converts regular URL to Scaper API's proxy URL
    """
    SCRAPER_API_KEY = os.environ.get('SCRAPER_API_KEY')
    if not SCRAPER_API_KEY:
        return url

    param = {'api_key': SCRAPER_API_KEY, 'url': url}
    return 'http://api.scraperapi.com/?' + urlencode(param)


def parse_price(price: str) -> Decimal:
    """
    Get price of a product from a given string
    """
    return Decimal(re.sub(r'[^\d.]', '', price))
