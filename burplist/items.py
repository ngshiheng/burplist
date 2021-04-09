import re

import scrapy
from itemloaders.processors import MapCompose, TakeFirst
from price_parser.parser import parse_price


def parse_name(name: str) -> str:
    """
    Remove units from the product name
    """
    removed_units = re.sub(r'\w+ml', '', name, flags=re.IGNORECASE)  # E.g.: "320ml"
    removed_brackets = re.sub(r'[\(\[].*?[\]\)]', '', removed_units)  # E.g.: "[CANS]"

    return removed_brackets.strip()


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
