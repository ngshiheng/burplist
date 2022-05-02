class HopShopLocator:
    """Locators for www.hopshop.com.sg"""

    # Locators for https://www.hopshop.com.sg/beer/
    products = '//li[@class="product"]'

    product_name = './/article/@data-name'
    product_url = './/a/@href'
    product_brand = './/article/@data-product-brand'
    product_style = './/article/@data-product-category'
    product_image_url = '//div[@class="card-img-container"]//img/@data-src'
    product_price = './/article/@data-product-price'

    next_page = '//li[@class="pagination-item pagination-item--next"]/a/@href'
