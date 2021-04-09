import unittest

from burplist.items import parse_name
from burplist.spiders.coldstorage import ColdStorageSpider


class BurplistTest(unittest.TestCase):
    def setUp(self):
        self.spider = ColdStorageSpider()

    def test_get_product_quantity(self):
        self.assertEqual(self.spider._get_product_quantity('Tiger Beer 24SX320ML'), 24)
        self.assertEqual(self.spider._get_product_quantity('Heineken Beer 20sX320ml'), 20)
        self.assertEqual(self.spider._get_product_quantity('Super Dry Draft 6sX350ml'), 6)
        self.assertEqual(self.spider._get_product_quantity('Carlsberg Beer Can 320ml'), 1)
        self.assertEqual(self.spider._get_product_quantity('Little Creatures Pale Ale 6s 330ml'), 6)
        self.assertEqual(self.spider._get_product_quantity('Carlsberg Green Label Beer 2sX500ml'), 2)
        self.assertEqual(self.spider._get_product_quantity('Brooklyn Defender IPA Bottle 4S 330ML'), 4)
        self.assertEqual(self.spider._get_product_quantity('Young Master Cha Chaan Teng Gose Bottle 330ml'), 1)
        self.assertEqual(self.spider._get_product_quantity('Somersby Seltzer Mango & Passionfruit Can 3s X 330ml'), 3)

    def test_parse_name(self):
        self.assertEqual(parse_name('Tiger Beer 24sX320ML'), 'Tiger Beer')
        self.assertEqual(parse_name('Bira 91 White Bottle 6sX330ml'), 'Bira 91 White Bottle')
        self.assertEqual(parse_name('Red Racer North West Pale Ale 320ml'), 'Red Racer North West Pale Ale')
        self.assertEqual(parse_name('Somersby Blackberry Cider [CANS] 330ml'), 'Somersby Blackberry Cider')
        self.assertEqual(parse_name('Founders Brewing Co. All Day IPA (568ml)'), 'Founders Brewing Co. All Day IPA')
        self.assertEqual(parse_name('Carlsberg Danish Can Beer - Wheat (Alcohol Free)'), 'Carlsberg Danish Can Beer - Wheat')
        # self.assertEqual(parse_name('Somersby Seltzer Mango & Passionfruit Can 3s X 330ml'), 'Somersby Seltzer Mango & Passionfruit Can') # BUG: Fix this
