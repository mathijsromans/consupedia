from questionmark import api
from .models import Product

class ProductService:
    def get_all_products(self):
        products_dict = api.search_product('pindakaas')
        products = self.get_or_create_from_json(products_dict)
        return products

    def get_or_create_from_json(self, products_dict):
        products = []
        for product_dict in products_dict["products"]:
            existing_products = Product.objects.filter(name=product_dict["name"])
            if existing_products.exists():
                # TODO: what if more than one product is found?
                product = existing_products[0]
            else:
                product = Product.objects.create(name=product_dict["name"])
            products.append(product)
        return products
