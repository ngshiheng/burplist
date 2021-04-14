import copy
import os

import scrapy.utils.log
from colorlog import ColoredFormatter

# Logging
color_formatter = ColoredFormatter(
    (
        '%(log_color)s%(levelname)-5s%(reset)s '
        '%(yellow)s[%(asctime)s]%(reset)s'
        '%(white)s %(name)s %(funcName)s %(bold_purple)s:%(lineno)d%(reset)s '
        '%(log_color)s%(message)s%(reset)s'
    ),
    datefmt='%y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG': 'blue',
        'INFO': 'bold_cyan',
        'WARNING': 'red',
        'ERROR': 'bg_bold_red',
        'CRITICAL': 'red,bg_white',
    }
)

_get_handler = copy.copy(scrapy.utils.log._get_handler)


def _get_handler_custom(*args, **kwargs):
    handler = _get_handler(*args, **kwargs)
    handler.setFormatter(color_formatter)
    return handler


scrapy.utils.log._get_handler = _get_handler_custom

# Burplist
BOT_NAME = 'burplist'
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')

SPIDER_MODULES = ['burplist.spiders']
NEWSPIDER_MODULE = 'burplist.spiders'

# Scraper API
SCRAPER_API_KEY = os.environ.get('SCRAPER_API_KEY')


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'burplist (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# Currently `CONCURRENT_REQUESTS` is set to 5 as we are using Scaper API free tier (https://www.scraperapi.com/pricing)
CONCURRENT_REQUESTS = 5 if SCRAPER_API_KEY is not None else 16
RETRY_TIMES = 5 if SCRAPER_API_KEY is not None else 0

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0 if SCRAPER_API_KEY is not None else 2
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    # 'burplist.middlewares.BurplistSpiderMiddleware': 543,
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # 'burplist.middlewares.BurplistDownloaderMiddleware': 543,
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}


# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
    'burplist.extensions.SentryLogging': -1,
    # 'scrapy.extensions.telnet.TelnetConsole': None,
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'burplist.pipelines.DuplicatePricePipeline': 300,
    'burplist.pipelines.NewProductPricePipeline': 400,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


# Splash
SPLASH_URL = 'http://localhost:8050'
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'

# Sentry
# https://stackoverflow.com/questions/25262765/handle-all-exception-in-scrapy-with-sentry
SENTRY_DSN = 'https://fa2a66ed7b8e4702b9c405f29a8b5df8@o545253.ingest.sentry.io/5704972'

# PostgreSQL
DATABASE_CONNECTION_STRING = '{drivername}://{user}:{password}@{host}:{port}/{db_name}'.format(
    drivername='postgresql',
    user=os.environ.get('PG_USERNAME', 'postgres'),
    password=os.environ.get('PG_PASSWORD'),
    host=os.environ.get('PG_HOST', 'localhost'),
    port=os.environ.get('PG_PORT', '5432'),
    db_name=os.environ.get('PG_DATABASE', 'burplist'),
)
