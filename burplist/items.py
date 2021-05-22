import scrapy
from itemloaders.processors import MapCompose, TakeFirst
from price_parser.parser import parse_price

from burplist.utils.parsers import parse_abv, parse_name, parse_volume


class ProductItem(scrapy.Item):
    platform = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst(),
    )

    name = scrapy.Field(
        input_processor=MapCompose(parse_name),
        output_processor=TakeFirst(),
    )
    url = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst(),
    )

    brand = scrapy.Field(
        output_processor=TakeFirst(),
    )
    style = scrapy.Field(
        output_processor=TakeFirst(),
    )
    origin = scrapy.Field(
        output_processor=TakeFirst(),
    )

    abv = scrapy.Field(
        input_processor=MapCompose(parse_abv),
        output_processor=TakeFirst(),
    )
    volume = scrapy.Field(
        input_processor=MapCompose(parse_volume),
        output_processor=TakeFirst(),
    )
    quantity = scrapy.Field(
        output_processor=TakeFirst(),
    )

    price = scrapy.Field(
        input_processor=MapCompose(parse_price),
        output_processor=TakeFirst(),
    )
