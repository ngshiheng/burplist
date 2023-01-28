# Define here the models for your spider middleware
# Useful for handling different item types with a single interface from itemadapter import is_item, ItemAdapter
#
# Please refer to the sqlalchemy documentation for information
# Reference: https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from burplist.middlewares.default import BurplistDownloaderMiddleware, BurplistSpiderMiddleware
from burplist.middlewares.delayed_requests import DelayedRequestsMiddleware
from burplist.middlewares.proxy import ProxyMiddleware

__all__ = [
    "BurplistDownloaderMiddleware",
    "BurplistSpiderMiddleware",
    "DelayedRequestsMiddleware",
    "ProxyMiddleware",
]
