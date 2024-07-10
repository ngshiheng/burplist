class HopShopLocator:
    """Locators for www.hopshop.com.sg"""

    # Locators for https://www.hopshop.com.sg/beer/
    beer_collection = "//ul[@id='categories-navList']//li[@class='navList-item']/a"
    products = '//li[@class="product"]'

    # Locators for products page
    # e.g. https://www.hopshop.com.sg/ipa/
    product_name = ".//h3[@class='card-title']/a/text()"
    product_url = ".//h3[@class='card-title']/a/@href"
    product_brand = ".//div[@class='card-text card-text--brand']/text()"

    product_image_url = './/div[@class="card-img-container"]/img/@src'
    product_price = ".//span[contains(@class, 'price price--withoutTax price--main')]/text()"

    next_page = '//li[@class="pagination-item pagination-item--next"]/a/@href'
