class TroubleBrewingLocator:
    """Locators for troublebrewing.com"""

    # Locators for https://troublebrewing.com/collections/trouble-beer-cider-hard-seltzer
    beer_collection = '//a[@class="product-link js-product-link"]'

    script_tag = '//script[contains(.,"var meta")]/text()'

    product_image_url = '//img[@class="product-single__photo__img"]//@src'
