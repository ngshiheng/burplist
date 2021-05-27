import logging
import re
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def parse_abv(raw_abv: str) -> Optional[float]:
    has_float_abv = re.search(r'(\d+\.\d+)', raw_abv)
    if has_float_abv:
        return float(has_float_abv.group(1))

    has_int_abv = re.search(r'(\d+)', raw_abv)
    if has_int_abv:
        return float(has_int_abv.group(1))

    return 0


def parse_name(raw_name: str) -> str:
    """
    Sanitize product name
    """
    logger.info(f'Parsing raw_name "{raw_name}".')

    remove_brackets = re.sub(r'[\(\[].*?[\]\)]', '', raw_name)  # E.g.: "Somersby Blackberry Cider [CANS] 330ml"
    remove_non_word_characters = re.sub(r'[^a-zA-Z0-9%.]', ' ', remove_brackets)
    remove_spaces = re.sub(' +', ' ', remove_non_word_characters)

    return remove_spaces.strip()


def parse_volume(raw_name: str) -> Optional[int]:
    """
    Get product volume from name
    """
    has_volume = re.search(r'(\d+) ?ml', raw_name, re.IGNORECASE)
    if has_volume:
        return int(has_volume.group(1))


def get_product_name_quantity(raw_name: str) -> Tuple[str, int]:
    logger.info(f'raw_name = "{raw_name}"')

    # Hite Jinro Extra Cold Beer Single Carton
    if 'carton' in raw_name.lower():
        return raw_name, 24

    # [Bundle of 24] Sapporo Premium Can Beer 330ml x 24cans (Expiry Jan 22)
    is_bundle = re.search(r'Bundle of (\d+)', raw_name, flags=re.IGNORECASE)
    if is_bundle:
        quantity = int(is_bundle.group(1))
        name = re.sub(is_bundle.group(), '', raw_name)
        return name, quantity

    # Carlsberg Danish Pilsner Beer Can 490ml (Pack of 24) Green Tab
    is_pack = re.search(r'Pack of (\d+)', raw_name, flags=re.IGNORECASE)
    if is_pack:
        quantity = int(is_pack.group(1))
        name = re.sub(is_pack.group(), '', raw_name)
        return name, quantity

    # Tiger Lager Beer Can 40x320ml, Guinness Foreign Extra Stout 24 x 500ml
    is_ml = re.search(r'(\d+)\s?x\s?\d{3}ml', raw_name, flags=re.IGNORECASE)
    if is_ml:
        quantity = int(is_ml.group(1))
        name = re.sub(is_ml.group(), '', raw_name)
        return name, quantity

    # Heineken Beer 330ml x 24 can
    is_ml_reverse = re.search(r'\d{3}ml\s?x\s?(\d+)', raw_name, flags=re.IGNORECASE)
    if is_ml_reverse:
        quantity = int(is_ml_reverse.group(1))
        name = re.sub(is_ml_reverse.group(), '', raw_name)
        return name, quantity

    # Blue Moon Belgian White Wheat Ale 355ml x 24 Bottles
    is_bottle = re.search(r'(\d+)(?:[A-Za-z\s]|\s)+Bottle', raw_name, flags=re.IGNORECASE)
    if is_bottle:
        quantity = int(is_bottle.group(1))
        name = re.sub(is_bottle.group(), '', raw_name)
        return name, quantity

    # San Miguel Pale Pilsen Can (24 cans x 330ml)
    is_cans = re.search(r'(\d+) Can', raw_name, flags=re.IGNORECASE)
    if is_cans:
        quantity = int(is_cans.group(1))
        name = re.sub(is_cans.group(), '', raw_name)
        return name, quantity

    return raw_name, 1
