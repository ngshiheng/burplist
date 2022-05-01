import unittest

from burplist.utils.proxy import get_proxy_url
from scrapy.utils.project import get_project_settings

settings = get_project_settings()


class TestProxy(unittest.TestCase):
    def test_get_proxy_url_returns_original_url_when_scraper_api_key_is_not_set(self) -> None:
        assert settings.get('SCRAPER_API_KEY') is None

        url = 'https://burplist.me'
        proxied_url = get_proxy_url(url)

        self.assertEqual(proxied_url, url)
