import logging
import re
from typing import Tuple

logger = logging.getLogger(__name__)


def get_product_name_quantity(raw_name: str) -> Tuple[str, int]:
    logger.info(f'raw_name = "{raw_name}"')

    # Hite Jinro Extra Cold Beer Single Carton
    if 'carton' in raw_name.lower():
        return raw_name, 24

    # Carlsberg Danish Pilsner Beer Can 490ml (Pack of 24) Green Tab
    is_pack = re.search(r'Pack of \d+', raw_name, flags=re.IGNORECASE)
    if is_pack:
        quantity = int(is_pack.group().split()[-1])
        name = re.sub(is_pack.group(), '', raw_name)
        return name, quantity

    # Tiger Lager Beer Can 40x320ml, Guinness Foreign Extra Stout 24 x 500ml
    is_ml = re.search(r'\d+\s?x\s?\d{3}ml', raw_name, flags=re.IGNORECASE)
    if is_ml:
        quantity = int(re.split('x', is_ml.group(), flags=re.IGNORECASE)[0])
        name = re.sub(is_ml.group(), '', raw_name)
        return name, quantity

    # Heineken Beer 330ml x 24 can
    is_ml_reverse = re.search(r'\d{3}ml\s?x\s?\d+', raw_name, flags=re.IGNORECASE)
    if is_ml_reverse:
        quantity = int(re.split('x', is_ml_reverse.group(), flags=re.IGNORECASE)[-1])
        name = re.sub(is_ml_reverse.group(), '', raw_name)
        return name, quantity

    # Blue Moon Belgian White Wheat Ale 355ml x 24 Bottles
    is_pack = re.search(r'\d+(?:[A-Za-z\s]|\s)+Bottles', raw_name, flags=re.IGNORECASE)
    if is_pack:
        quantity = int(is_pack.group().split()[0])
        name = re.sub(is_pack.group(), '', raw_name)
        return name, quantity

    # San Miguel Pale Pilsen Can (24 cans x 330ml)
    is_cans = re.search(r'\d+ Cans', raw_name, flags=re.IGNORECASE)
    if is_cans:
        quantity = int(is_cans.group().split()[0])
        name = re.sub(is_cans.group(), '', raw_name)
        return name, quantity

    return raw_name, 1
