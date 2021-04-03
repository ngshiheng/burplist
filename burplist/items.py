import enum

import scrapy
from itemloaders.processors import MapCompose, TakeFirst

from burplist.utils.proxy import parse_price


class Unit(enum.Enum):
    SINGLE = 'Single'
    SIXPACK = 'Six Pack'
    CARTON = 'Carton'


class ProductItem(scrapy.Item):
    name = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst(),
    )

    price = scrapy.Field(
        input_processor=MapCompose(parse_price),
        output_processor=TakeFirst(),
    )

    unit = scrapy.Field(
        output_processor=TakeFirst(),
    )

    url = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst(),
    )
