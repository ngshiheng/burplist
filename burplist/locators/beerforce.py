class BeerForceLocator:
    """Locators for beerforce.sg"""

    # Locators for https://beerforce.sg/pages/all-styles
    beer_collection = '//a[@class="collection-list__link"]/@href'

    # Locators for products page by style,
    # e.g. https://beerforce.sg/collections/ipa
    product_details = '//div[contains(@class,"product-card js")]/div[@class="product-card__details"]'
    product_media = '//div[contains(@class,"product-card-top")]'

    product_name = './/h2[contains(@class,"product-card__title")]/text()'
    product_url = './a/@href'
    product_brand = './/p[contains(@class,"product-card__vendor")]/text()'
    product_price = './/span[@class="money"]/text()'

    next_page = '//span[@class="next"]/a/@href'

    # Locators for product detail page,
    # e.g. https://beerforce.sg/collections/ipa/products/youngmaster1842islandipa
    product_info = '//div[@class="product-single__content-text rte"]//*[b or strong]//text()'
    product_image_url = '//img[@class="product-single__photo__img js-pswp-img"]/@src'
