from questionmark import api
from .models import Product, Score


class ProductService:

    def get_all_products(self):
        self.update_products_from_api("pindakaas")
        self.update_products_from_api("spinazie")

        return Product.objects.all()

    def update_products_from_api(self, category):
        products_dict = api.search_product(category)
        products = []
        for product_dict in products_dict["products"]:
            existing_products = Product.objects.filter(name=product_dict["name"])
            if existing_products.exists():
                # TODO: what if more than one product is found?
                product = existing_products[0]
            else:
                product = Product.objects.create(name=product_dict["name"])
            product = self.map_to_product(product, product_dict)
            products.append(product)
        return products

    def map_to_product(self, product, product_dict):
        theme_scores = product_dict["theme_scores"]
        personal_health_score = product_dict["personal_health_score"]
        
        if theme_scores or personal_health_score:
            product.scores = Score.objects.create()

        if theme_scores:
            for score in theme_scores:
                if score["theme_key"] == "environment":
                    product.scores.environment = score["score"]
                elif score["theme_key"] == "social":
                    product.scores.social = score["score"]
                elif score["theme_key"] == "animals":
                    product.scores.animals = score["score"]
        if personal_health_score:
            product.scores.personal_health_score = personal_health_score

        if product.scores:
            product.scores.save()

        product.save()
        return product

