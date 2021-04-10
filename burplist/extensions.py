import sentry_sdk
from scrapy.exceptions import NotConfigured
from scrapy.utils.project import get_project_settings


class SentryLogging(object):
    """
    Send exceptions and errors to Sentry.
    """
    @classmethod
    def from_crawler(cls, crawler):
        sentry_dsn = crawler.settings.get('SENTRY_DSN', None)
        if sentry_dsn is None:
            raise NotConfigured('Sentry DSN is missing.')

        extension = cls()
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=get_project_settings().get('ENVIRONMENT'),
        )

        return extension
