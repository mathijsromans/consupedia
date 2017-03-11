from questionmark import api
from .models import Product, Score
from .questionmarkmapper import QuestionmarkMapper
from .rating import rating_manager


class ProductService:

    def get_all_products(self):
        self.update_products_from_questionmarkapi("pindakaas")

        return Product.objects.all()

    def update_products_from_questionmarkapi(self, category):
        products_dict = api.search_product(category)
        products = []
        for product_dict in products_dict["products"]:
            product, created = Product.objects.get_or_create(name=product_dict["name"])
            product = QuestionmarkMapper().map_to_product(product, product_dict)
            print(rating_manager.get_avarage_rating(product))
            products.append(product)
        return products
