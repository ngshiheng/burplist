from typing import Any, Generator
from urllib.parse import urlencode

import scrapy

from burplist.items import ProductLoader
from burplist.utils.parsers import parse_brand, parse_quantity


class AlcohaulSpider(scrapy.Spider):
    """Scrape data from Alcohaul API

    https://alcohaul.sg/
    """

    name = "alcohaul"
    base_url = "https://alcohaul.sg/api/productlist?"

    params: dict[str, Any] = {
        "skip": 0,
        "limit": 50,
        "parent": "5f7edae59ae56e6d7b8b456d",
        "filter": "a-z",
        "child": "5f7edb459ae56e6d7b8b45df",
    }

    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        url = self.base_url + urlencode(self.params)
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response) -> Generator[scrapy.Request, None, None]:
        """
        @url https://alcohaul.sg/api/productlist?skip=0&limit=50&parent=5f7edae59ae56e6d7b8b456d&filter=a-z&child=5f7edb459ae56e6d7b8b45df
        @returns items 1 50
        @returns requests 1
        @scrapes platform name url volume quantity price
        """
        data = response.json()
        products = data["items"]

        if products:
            for product in products:
                if int(product["quantity"]) < 1:  # NOTE: `quantity` could be `int` or `str` from API
                    continue

                loader = ProductLoader()
                slug = product["slug"]

                loader.add_value("platform", self.name)
                loader.add_value("name", product["name"])
                loader.add_value("url", f"https://alcohaul.sg/products/{slug}")

                loader.add_value("brand", parse_brand(product["name"]))
                loader.add_value("origin", product.get("country"))
                loader.add_value("style", product.get("type"))

                loader.add_value("abv", product.get("alcohol"))
                loader.add_value("volume", product["name"])
                loader.add_value("quantity", parse_quantity(product["name"]))

                image_url = product.get("imageFiles")[0]["source"]
                loader.add_value("image_url", f"https://alcohaul.sg/products/i/{image_url}")

                loader.add_value("price", product["smartPrice"])

                yield loader.load_item()

            self.params["skip"] += 50
            next_page = self.base_url + urlencode(self.params)
            yield response.follow(next_page, callback=self.parse)
