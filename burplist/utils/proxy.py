import logging
from urllib.parse import urlencode

from scrapy.utils.project import get_project_settings

logger = logging.getLogger(__name__)

settings = get_project_settings()


def get_proxy_url(url: str) -> str:
    """
    We send all our requests to https://www.scraperapi.com/ API endpoint in order use their proxy servers
    This function converts regular URL to Scaper API's proxy URL
    """
    scraper_api_key = settings.get('SCRAPER_API_KEY')
    if not scraper_api_key:
        logger.warning('Scraper API key not set.', extra=dict(url=url))
        return url

    proxied_url = 'http://api.scraperapi.com/?' + urlencode({'api_key': scraper_api_key, 'url': url})
    logger.info(f'Scraping using Scraper API proxied URL <{proxied_url}>.')
    return proxied_url
