class ColdStorageLocator:
    """Locators for coldstorage.com.sg"""

    # Locators for https://coldstorage.com.sg/beers-wines-spirits/beer-cider/craft-beers
    products = '//div[@class="product_box"]'

    product_name = './/div[@class="product_name "]/text()'
    product_url = './/a[@class="product-link"]/@href'
    product_brand = './/div[@class="category-name"]/b/text()'
    product_price = './/div[@data-price]/text()'
    product_image_url = './/div[@class="product_images"]//img//@src'

    next_page = '//li[@class="next"]/a/@href'
