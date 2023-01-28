class CraftBeerSGLocator:
    """Locators for craftbeersg.com"""

    # Locators for https://www.craftbeersg.com/product-category/beer/
    raw_html = '//div[@id="primary"]//script[@type="text/template"]/text()'
    beer_collection = '//div[@class="product-image"]/a/@href'

    # Locators for products page
    # e.g. https://www.craftbeersg.com/product/mango-into-a-hop-field/
    product_name = '//h2[@class="product_title entry-title show-product-nav"]/text()'
    product_brand = '//span[text()="Brand: "]/a/text()'
    product_origin = '//span[text()="Country: "]/a/text()'
    product_image_url = '//img[@class="woocommerce-main-image img-responsive"]/@src'

    product_variants = '//div[@class="row"]//div[@class="variable-item-contents"]'
    product_price = './/span[@class="woocommerce-Price-amount amount"]//bdi/text()'
    product_display_unit = (
        './/span[@class="variable-item-span variable-item-span-button"]/text()'
    )
