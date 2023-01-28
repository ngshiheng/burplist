class ThirstyLocator:
    """Locators for www.thirsty.com.sg"""

    # Locators for https://www.thirsty.com.sg/collections/beer
    beer_collection = '//div[@class="boost-pfs-filter-product-bottom"]//a'
    next_page = '//a[@aria-label="Page Next"]'

    # Locators for products page
    # e.g. https://www.thirsty.com.sg/collections/beer/products/4-pines-australian-pacific-ale-can
    product_name = '//h1[@class="h3 tl c-white"]/text()'

    product_brand = '//h2[@class="h3 mb-10 d-mb-15"]/text()'
    product_origin = '//div[text()="Birthplace"]/following-sibling::div/text()'
    product_style = '//div[text()="Style"]/following-sibling::div/text()'

    product_abv = '//div[text()="Alcohol Percentage"]/following-sibling::div/text()'

    product_variants = "//div[@data-value]"
    product_display_unit = './/div[@class="mb-5 opacity-5 p3 d-mb-0"]/text()'

    product_price = './/div[@class="var-price h6 d-ml-25"]/text()'

    product_image_url = '//img[@class="image loaded"]/@src'
