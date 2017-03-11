from questionmark import api
from .models import Product

class ProductService:
    def get_all_products(self):
        products_dict = api.search_product('pindakaas')
        products = self.create_from_json(products_dict)
        return products

    def create_from_json(self, products_dict):
        products = [];
        for product_dict in products_dict["products"]:
            if not Product.objects.filter(name=product_dict["name"]).exists():
                product = Product.objects.create(name=product_dict["name"])
                products.append(product)
        return products
