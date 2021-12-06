class ThirstyLocator:
    """Locators for www.thirsty.com.sg"""

    # Locators for https://www.thirsty.com.sg/pages/shop-by-style
    beer_collection = '//a[@class="link-3 color-header"]'

    # Locators for products page, e.g. https://www.thirsty.com.sg/collections/lager
    products = '//div[@class="product-each-top cf"]'
    product_title = './/a[@class="link-3 color-header"]/@href'
    product_prices = './/span[@class="color-header body-s"]/text()'
    product_display_units = './/p[contains(@class,"product-option-title body-xxs ml-5")]'

    product_name = './/a[@class="link-3 color-header"]/text()'
    product_brand = './/a[@class="body-xs color-text"]/text()'
    product_abv = './/span[@class="alcohol color-text body-xs mr-5"]/text()'
    product_volume = './/span[@class="volume color-text body-xs tablet-mr-5"]/text()'
    product_image_url = './/img[@class="image image-option primary lazy"]/@data-lazy'
