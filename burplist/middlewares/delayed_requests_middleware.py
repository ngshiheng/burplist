from twisted.internet import reactor
from twisted.internet.defer import Deferred


class DelayedRequestsMiddleware(object):
    """
    Usage e.g.:
    yield scrapy.Request(url='http://example.com/page/1/', meta={ 'delay_request_by': 5 })

    Reference: https://stackoverflow.com/questions/19135875/add-a-delay-to-a-specific-scrapy-request/64903556#64903556
    """

    def process_request(self, request, spider):
        delay_s = request.meta.get('delay_request_by', 5)
        spider.logger.info(f'Delay request for {delay_s} seconds...')

        deferred = Deferred()
        reactor.callLater(delay_s, deferred.callback, None)
        return deferred
