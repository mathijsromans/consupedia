from questionmark import api
from .models import Product, Category, Score
from questionmark.jumbo_scraper import JumboScraper
from .questionmarkmapper import QuestionmarkMapper


class ProductService:

    @staticmethod
    def get_all_products(search_query):
        if search_query:
            return ProductService.update_products_from_questionmarkapi(search_query)
        return Product.objects.all()

    @staticmethod
    def update_products_from_questionmarkapi(search_name):
        products_dict = api.search_product(search_name)
        name_price_list = JumboScraper().get_search_result(search_name)
        products = []
        for product_dict in products_dict["products"]:
            product, created = Product.objects.get_or_create(name=product_dict["name"])
            product = QuestionmarkMapper().map_to_product(product, product_dict)
            for name_price in name_price_list:
                name = "Jumbo " + product.name.replace("0 g", "0g")
                if name in name_price:
                    product.price = int(name_price[name])
                    product.save()
            products.append(product)
        return products
