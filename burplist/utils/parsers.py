import logging
import re
from typing import Optional

from burplist.utils.styles import styles

logger = logging.getLogger(__name__)


def parse_name(raw_name: str) -> str:
    """
    Sanitize product name
    """
    logger.info(f'Parsing raw_name "{raw_name}".')

    remove_brackets = re.sub(r'[\(\[].*?[\]\)]', '', raw_name)  # E.g.: "Somersby Blackberry Cider [CANS] 330ml"
    remove_non_word_characters = re.sub(r'[^a-zA-Z0-9%.]', ' ', remove_brackets)
    remove_spaces = re.sub(' +', ' ', remove_non_word_characters)

    return remove_spaces.strip()


def parse_style(raw_style: str) -> Optional[str]:
    return next((style for style in styles if style.lower() in raw_style.lower()), None)


def parse_origin(raw_origin: str) -> Optional[str]:
    pass


def parse_abv(raw_abv: str) -> Optional[float]:
    has_float_abv = re.search(r'(\d{1,2}\.\d{1,2})%', raw_abv)
    if has_float_abv:
        return float(has_float_abv.group(1))

    has_int_abv = re.search(r'(\d{1,2})%', raw_abv)
    if has_int_abv:
        return float(has_int_abv.group(1))


def parse_volume(raw_name: str) -> Optional[int]:
    """
    Get product volume from name
    """
    has_volume = re.search(r'(\d{3}) ?ml', raw_name, flags=re.IGNORECASE)
    if has_volume:
        return int(has_volume.group(1))
