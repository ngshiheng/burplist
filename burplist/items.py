import scrapy
from itemloaders.processors import Identity, MapCompose, TakeFirst
from price_parser.parser import parse_price
from scrapy.loader import ItemLoader

from burplist.utils.parsers import parse_abv, parse_name, parse_volume


class ProductItem(scrapy.Item):
    platform = scrapy.Field()

    name = scrapy.Field(input_processor=MapCompose(str.strip, parse_name))
    url = scrapy.Field()

    brand = scrapy.Field()
    style = scrapy.Field()
    origin = scrapy.Field()

    abv = scrapy.Field(input_processor=MapCompose(str.strip, parse_abv))
    volume = scrapy.Field(input_processor=MapCompose(str.strip, parse_volume))
    quantity = scrapy.Field(input_processor=Identity())

    image_url = scrapy.Field()

    price = scrapy.Field(input_processor=MapCompose(parse_price))


class ProductLoader(ItemLoader):
    default_item_class = ProductItem

    default_input_processor = MapCompose(str.strip)
    default_output_processor = TakeFirst()
