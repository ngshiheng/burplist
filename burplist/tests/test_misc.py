import unittest

from burplist.utils.misc import remove_stale_products_prices


class TestMisc(unittest.TestCase):
    def test_prevent_remove_stale_products_from_deleting_all(self) -> None:
        self.assertRaises(AssertionError, remove_stale_products_prices, 0)
