class GiantLocator:
    """Locators for giant.sg"""

    # Locators for https://giant.sg/beers-wines-spirits/beers-ciders
    products = '//div[@class="product_box"]'

    product_name = './/a[@class="product-link"]/text()'
    product_url = './/a[@class="product-link"]/@href'
    product_brand = './/a[@class="to-brand-page"]/text()'
    product_price = './/div[@class="content_price"]//@data-price'

    product_image_url = './/div[@class="product_images"]//@src'

    next_page = '//li[@class="next"]/a/@href'
