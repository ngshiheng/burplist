import re

import scrapy
from itemloaders.processors import MapCompose, TakeFirst
from price_parser.parser import parse_price


def parse_name(name: str) -> str:

    name = re.sub(r'[,]$', '', name.strip())  # Remove trailing comma
    remove_brackets = re.sub(r'[\(\[].*?[\]\)]', '', name)  # E.g.: "Somersby Blackberry Cider [CANS] 330ml"
    remove_units = re.sub(r' \d*?s?\s?x?\s?\S+(ml)', '', remove_brackets, flags=re.IGNORECASE)  # E.g.: "Red Racer North West Pale Ale 320ml"
    remove_abv = re.sub(r'ABV\s?\d+.?\d*%', '', remove_units, flags=re.IGNORECASE)  # E.g.: Stone Sublimely Self Righteous Black IPA ABV 8.7%
    remove_trailing_s = re.sub(r'\d+s$', '', remove_abv, flags=re.IGNORECASE)  # FIXME: Figure out a better regex

    remove_non_word_char = re.sub(r'[^a-zA-Z0-9%.]', ' ', remove_trailing_s)

    # remove_trailing_comma = re.sub(r',$', '', remove_trailing_s)  # Remove trailing comma
    remove_spaces = re.sub(' +', ' ', remove_non_word_char)

    return remove_spaces.strip()


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
