import unittest
from decimal import Decimal

from burplist.utils.parsers import quantize_price
from price_parser.parser import Price


class TestParsers(unittest.TestCase):
    def test_quantizing_price_object_from_parse_price(self) -> None:
        amount_string1 = "2.2399999999999998"
        price1 = Price.fromstring(amount_string1)

        self.assertIsInstance(quantize_price(price1), Price)
        self.assertEqual(quantize_price(price1).amount, Decimal("2.24"))

        amount_string2 = "26.459999999999997"
        price2 = Price.fromstring(amount_string2)

        self.assertIsInstance(quantize_price(price2), Price)
        self.assertEqual(quantize_price(price2).amount, Decimal("26.46"))
