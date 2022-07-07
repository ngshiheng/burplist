class TheGreatBeerExperimentLocator:
    """Locators for greatbeerexperiment.com"""

    # Locators for https://greatbeerexperiment.com/collections
    beer_collection = "//li[contains(@class,'brewery') and contains(./details, ' ')]//li/a"

    # Locators for products page
    # e.g. https://greatbeerexperiment.com/collections/beers-from-belgium
    products = "//div[@class='productitem']"
    product_name = './/h2[@class="productitem--title"]/a/text()'
    product_url = './/h2[@class="productitem--title"]/a/@href'
    product_price = './/div[@class="productitem--actions"]//div[@class="price__current--hidden"]/span[@class="money"]/text()'
    product_image_url = './/img[@class="productitem--image-primary" and @data-rimg-scale]/@src'

    next_page = '//li[@class="pagination--next"]/a/@href'
