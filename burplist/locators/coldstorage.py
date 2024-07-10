class ColdStorageLocator:
    """Locators for coldstorage.com.sg"""

    # Locators for https://coldstorage.com.sg/en/category/100001-100044-100386/1.html
    products = '//div[@class="mg-r-10"]'

    product_name = './/div[@class="name"]/text()'
    product_url = "./a"
    product_price = ".//span[@class='price']/text()"

    next_page = '//a[@class="next cursor btn-box op-btn"]/@href'
