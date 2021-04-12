import re

import scrapy
from itemloaders.processors import MapCompose, TakeFirst
from price_parser.parser import parse_price


def parse_name(name: str) -> str:
    """
    Remove units from the product name
    """
    remove_dashes = re.sub(r'-[\s?]', '', name)
    remove_units = re.sub(r'\d*\sx?\s?\w+ml', '', remove_dashes, flags=re.IGNORECASE)  # E.g.: "Red Racer North West Pale Ale 320ml"
    remove_brackets = re.sub(r'[\(\[].*?[\]\)]', '', remove_units)  # E.g.: "Somersby Blackberry Cider [CANS] 330ml"
    remove_trailing_s = re.sub(r'\d+s$', '', remove_brackets, flags=re.IGNORECASE)  # FIXME: Figure out a better regex

    return remove_trailing_s.strip()


class ProductItem(scrapy.Item):
    vendor = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst(),
    )

    name = scrapy.Field(
        input_processor=MapCompose(parse_name),
        output_processor=TakeFirst(),
    )

    price = scrapy.Field(
        input_processor=MapCompose(parse_price),
        output_processor=TakeFirst(),
    )

    quantity = scrapy.Field(
        output_processor=TakeFirst(),
    )

    url = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst(),
    )
