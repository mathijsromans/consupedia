from django.db import transaction

from questionmark import api, jumbo
from .models import Product, Category, Score, Ingredient, Recipe
from .mappers import QuestionmarkMapper, JumboMapper
from collections import defaultdict

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
                print(name + "   ----   " + jumbo_result['name'])
                if jumbo_result['name'] == name:
                    jumbo_mapper.map_to_product(product, jumbo_result)
            products.append(product)
        return products

class RecipeService():

    @staticmethod
    def create_recipe( name,
                       author_if_user,
                       source_if_not_user,
                       number_persons,
                       preparation_time_in_min,
                       preparation,
                       ingredient_input ):
        test_ingredients = [
            [4, 'uien'],
            [500, 'g', 'preien'],
            [40, 'g', 'boter'],
            [2, 'el', 'olijfolie'],
            [1, 'el', 'gedroogde tijm'],
            [2, 'blaadjes', 'laurierblaadjes'],
            [198, 'g', 'corned beef'],
            [2, 'kg', 'gezeefde tomaten'],
            [1, 'kg', 'half-om-halfgehakt']]

        if not ingredient_input:
            ingredient_input = test_ingredients
        print('create recipe: ' + str(ingredient_input))
        new_recipe = Recipe.objects.create(name = name,
                                           author_if_user=author_if_user,
                                           source_if_not_user = source_if_not_user,
                                           number_persons = number_persons,
                                           preparation_time_in_min = preparation_time_in_min,
                                           preparation = preparation)
        for ing in ingredient_input:
            if len(ing) != 3:
                continue
            products = ProductService().get_all_products(ing[2])
            if len(products) == 0:
                continue
            cat_dict = defaultdict(int)
            for p in products:
                cat_dict[p.category] += 1
            max_cat = max(cat_dict.items(), key=(lambda a: a[1]))
            print(max_cat[0])
            Ingredient.objects.create(quantity=ing[0], unit=Ingredient.NO_UNIT, category=max_cat[0], recipe = new_recipe)
