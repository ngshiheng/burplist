import unittest
from dataclasses import dataclass
from decimal import Decimal

from burplist.utils.parsers import parse_quantity, quantize_price
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

    def test_parse_quantity_from_product_name(self) -> None:
        @dataclass
        class TestCase:
            name: str
            expected: int

        test_cases = [
            TestCase(name="Carlsberg 490ml x 24 Cans (BBD: Oct 2021)", expected=24),
            TestCase(name="Carlsberg Danish Pilsner Beer Can 490ml (Pack of 48) Green", expected=48),
            TestCase(name="Carlsberg Smooth Draught Beer Can, 320ml [Bundle of 12]", expected=12),
            TestCase(name="Heineken Beer 330ml x 24 can", expected=24),
        ]

        for test in test_cases:
            self.assertEqual(parse_quantity(test.name), test.expected)
