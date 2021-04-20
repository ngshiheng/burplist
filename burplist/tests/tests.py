import unittest

from burplist.items import parse_name
from burplist.spiders.brewerkz import BrewerkzSpider
from burplist.spiders.coldstorage import ColdStorageSpider


class BurplistTest(unittest.TestCase):
    def test_parse_name(self):
        # coldstorage
        self.assertEqual(parse_name('Tiger Beer 24sX320ML'), 'Tiger Beer')
        self.assertEqual(parse_name('Red Racer North West Pale Ale 320ml'), 'Red Racer North West Pale Ale')
        self.assertEqual(parse_name('Somersby Blackberry Cider [CANS] 330ml'), 'Somersby Blackberry Cider')
        self.assertEqual(parse_name('Founders Brewing Co. All Day IPA (568ml)'), 'Founders Brewing Co. All Day IPA')
        self.assertEqual(parse_name('Carlsberg Danish Can Beer - Wheat (Alcohol Free)'), 'Carlsberg Danish Can Beer Wheat')
        self.assertEqual(parse_name('Somersby Seltzer Mango & Passionfruit Can 3s X 330ml'), 'Somersby Seltzer Mango & Passionfruit Can')
        self.assertEqual(parse_name('Fleet Clouds Can 1s 330ml'), 'Fleet Clouds Can')

        # brewerkz
        self.assertEqual(parse_name('India Pale Ale - 4 x 330ml'), 'India Pale Ale')
        self.assertEqual(parse_name('Afterburner Pacific Pale Ale - 6 x 330ml'), 'Afterburner Pacific Pale Ale')
        self.assertEqual(parse_name('Circuit Breaker (New England IPA)- 6 x 330ml'), 'Circuit Breaker')
        self.assertEqual(parse_name('Green Gunpowder Double IPA Series: Resin Bomb - 24 x 330ml'), 'Green Gunpowder Double IPA Series: Resin Bomb')

        # thirsty
        self.assertEqual(parse_name('21ST AMENDMENT BREW FREE! OR DIE IPA'), '21ST AMENDMENT BREW FREE! OR DIE IPA')

        # hopshop
        self.assertEqual(parse_name('Moon Dog The Duke Of Chifley BA Barley Wine ABV 12.2%'), 'Moon Dog The Duke Of Chifley BA Barley Wine')
        self.assertEqual(parse_name('Epic Alien Invasion Double IPA ABV 8%'), 'Epic Alien Invasion Double IPA')
        self.assertEqual(parse_name('Mikkeller George Bourbon Barrel Aged Imperial Stout ABV 13.8%'), 'Mikkeller George Bourbon Barrel Aged Imperial Stout')
        self.assertEqual(parse_name('Rocky Ridge Pine On You Crazy Diamond Imperial IPA ABV 8.85%'), 'Rocky Ridge Pine On You Crazy Diamond Imperial IPA')
        self.assertEqual(parse_name('Rocky Ridge Raspberry Imperial Berliner Recipe v2.1 375mL ABV 6.5%	'), 'Rocky Ridge Raspberry Imperial Berliner Recipe v2.1')


class ColdStorageSpiderTest(unittest.TestCase):
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


class BrewerkzSpiderTest(unittest.TestCase):
    def setUp(self):
        self.spider = BrewerkzSpider()

    def test_get_product_quantity(self):
        self.assertEqual(self.spider._get_product_quantity('India Pale Ale - 4 x 330ml'), 4)
        self.assertEqual(self.spider._get_product_quantity('Islander Brew: Bukit Manis (6 x 330ml)'), 6)
        self.assertEqual(self.spider._get_product_quantity('Islander Brew: Mixed 4pack (4 x 330ml)'), 4)
        self.assertEqual(self.spider._get_product_quantity('Afterburner Pacific Pale Ale - 6 x 330ml'), 6)
        self.assertEqual(self.spider._get_product_quantity('Circuit Breaker (New England IPA)- 6 x 330ml'), 6)
        self.assertEqual(self.spider._get_product_quantity('Green Gunpowder Double IPA Series: Resin Bomb - 24 x 330ml'), 24)
