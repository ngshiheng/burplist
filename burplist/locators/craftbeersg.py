class CraftBeerSGLocator:
    """Locators for craftbeersg.com"""

    # Locators for https://www.craftbeersg.com/collections
    beer_collection = "//details[@id='Details-HeaderMenu-5']//a[@class='header__menu-item list-menu__item link link--text focus-inset caption-large']"

    # Locators for collection page
    # e.g. https://www.craftbeersg.com/collections/lager
    products = "//li[@class='grid__item']"
    product_name_brand = ".//h3[@class='card__heading h5']/a//text()"
    product_url = ".//h3[@class='card__heading h5']//@href"
    product_image_url = ".//*[@class='media media--transparent media--hover-effect']//img//@src"
    product_price = ".//*[@class='price-item price-item--sale price-item--last']"

    next_page = "//*[@aria-label='Next page']/@href"
