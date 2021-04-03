import os
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


def remove_dollar_sign(price: str) -> str:
    """
    Remove dollar sign from a string
    """
    return price.replace('$', '')
