from django.db import transaction

from questionmark import api, jumbo
from .models import Product, Category, Score
from .mappers import QuestionmarkMapper, JumboMapper

class ProductService:

    @staticmethod
    def get_all_products(search_query):
        if search_query:
            return ProductService.update_products_from_questionmarkapi(search_query)
        return Product.objects.all()

    @staticmethod
    @transaction.atomic
    def update_products_from_questionmarkapi(search_name):
        qm_mapper = QuestionmarkMapper()
        jumbo_mapper = JumboMapper()

        products_dict = api.search_product(search_name)
        jumbo_results = jumbo.search_product(search_name)
        products = []
        for product_dict in products_dict["products"]:
            product, created = Product.objects.get_or_create(name=product_dict["name"])
            product = qm_mapper.map_to_product(product, product_dict)
            for jumbo_result in jumbo_results:
                name = "Jumbo " + product.name.replace("0 g", "0g")
                if jumbo_result['name'] == name:
                    jumbo_mapper.map_to_product(product, jumbo_result)
            products.append(product)
        return products


