from burplist.utils.misc import remove_stale_products_prices
from scrapy.commands import ScrapyCommand


class Command(ScrapyCommand):
    requires_project = False
    default_settings = {'LOG_ENABLED': True}

    def syntax(self) -> str:
        return '[options]'

    def short_desc(self) -> str:
        return 'Remove stale products and prices which are not updated for N number of days'

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)

        parser.add_option(
            '-d', '--days', dest='days', type=int, default=7,
            help='N number of days in integer where the products are not updated',
        )

    def run(self, args, opts) -> None:
        remove_stale_products_prices(opts.days)
