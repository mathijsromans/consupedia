from questionmark import api
from .models import Product
from .questionmarkmapper import QuestionmarkMapper


class ProductService:

    @staticmethod
    def get_all_products():
        ProductService.update_products_from_questionmarkapi("tomatenpuree")

        return Product.objects.all()

    @staticmethod
    def update_products_from_questionmarkapi(category):
        products_dict = api.search_product(category)
        products = []
        for product_dict in products_dict["products"]:
            product, created = Product.objects.get_or_create(name=product_dict["name"])
            product = QuestionmarkMapper().map_to_product(product, product_dict)
            products.append(product)
        return products
