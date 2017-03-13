from django.db import transaction

import re
from questionmark import api, jumbo, ah
from .models import Product, Category, Score, Ingredient, Recipe
from .mappers import QuestionmarkMapper, RetailerMapper
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

        products_dict = api.search_product(search_name)
        jumbo_results = jumbo.search_product(search_name)
        ah_results = ah.search_product(search_name)

        product_ids = []
        mapper = RetailerMapper()
        for product_dict in products_dict['products']:
            product, created = Product.objects.get_or_create(name=product_dict['name'])
            product = qm_mapper.map_to_product(product, product_dict)

            # TODO: if both have a match, last price wins
            ProductService.enrich_product_data(mapper, product, jumbo_results)
            ProductService.enrich_product_data(mapper, product, ah_results)

            product_ids.append(product.id)

        return Product.objects.filter(id__in=product_ids)

    @staticmethod
    def get_or_create_unknown_category():
        category, created = Category.objects.get_or_create(name='Unknown category')
        if created:
            product, created = Product.objects.get_or_create(name='Unknown product')
            product.category = category
        return category

    @staticmethod
    def enrich_product_data(mapper, product, retailer_results):
        for retailer_result in retailer_results:
            if ProductService.matches_name(retailer_result['name'], product.name):
                mapper.map_to_product(product, retailer_result)


    @staticmethod
    def matches_name(retailer_name, name):
        if retailer_name == name:
            return True

        retailer_name = retailer_name.replace('\xad', '')
        retailer_name = retailer_name.replace(' ', '')

        name = re.sub('\(.*\)', '' , name)
        name = name.replace(' ', '')

        if retailer_name == name:
            return True

        brands = ['Hero', 'Jumbo', 'AH']
        for brand in brands:
            retailer_name = retailer_name.replace(brand, '').strip()

        if retailer_name == name:
            return True


    @staticmethod
    def contains_jumbo(product_dict):
        # Method is not being used right now, since sometimes Jumbo is not present as a retailer or brand
        # but the product is still available on the Jumbo site
        contains = False
        if product_dict['retailers']:
            for retailer in product_dict['retailers']:
                if retailer['name'] == 'Jumbo':
                    contains = True
                    break;
        if product_dict['brand']:
            if product_dict['brand']['name'] == 'Jumbo':
                contains = True
        return contains


class RecipeService():

    @staticmethod
    def get_quantity_and_unit( quantity, unit_text ):
        if unit_text == '-' or unit_text == 'blaadjes':
            return quantity, Ingredient.NO_UNIT
        if unit_text == 'g':
            return quantity, Ingredient.GRAM
        if unit_text == 'kg':
            return 1000*quantity, Ingredient.GRAM
        if unit_text == 'el':
            return quantity, Ingredient.EL
        print('UNKNOWN UNIT : ' + unit_text)
        return quantity, Ingredient.NO_UNIT

    @staticmethod
    def create_recipe( name,
                       author_if_user,
                       source_if_not_user,
                       number_persons,
                       preparation_time_in_min,
                       preparation,
                       ingredient_input ):
        test_ingredients = [
            [4, '-', 'uien'],
            [500, 'g', 'preien'],
            [40, 'g', 'boter'],
            [2, 'el', 'olijfolie'],
            [1, 'el', 'gedroogde tijm'],
            [2, 'blaadjes', 'laurierblaadjes'],
            [198, 'g', 'corned beef'],
            [2, 'kg', 'gezeefde tomaten'],
            [1, 'kg', 'half-om-halfgehakt']]

        if Recipe.objects.filter(name=name).first():
            # recipe already exists
            return
        if not ingredient_input:
            ingredient_input = test_ingredients
        print('Creating recipe with ingredients: ' + str(ingredient_input))
        new_recipe = Recipe.objects.create(name = name,
                                           author_if_user=author_if_user,
                                           source_if_not_user = source_if_not_user,
                                           number_persons = number_persons,
                                           preparation_time_in_min = preparation_time_in_min,
                                           preparation = preparation)
        for ing in ingredient_input:
            if len(ing) != 3:
                continue
            quantity = 0
            unit = Ingredient.NO_UNIT
            category = ProductService.get_or_create_unknown_category()
            products = ProductService().get_all_products(ing[2])
            if products:
                cat_dict = defaultdict(int)
                for p in products:
                    cat_dict[p.category] += 1
                category = max(cat_dict.items(), key=(lambda a: a[1]))[0]
                if not category:
                    category = ProductService.get_or_create_unknown_category()
            quantity, unit = RecipeService.get_quantity_and_unit( ing[0], ing[1])
            print('Using ingredient ' + str(quantity) + ' ' + str(unit) + ' ' + str(category))
            Ingredient.objects.create(quantity=quantity, unit=unit, category=category, recipe = new_recipe)
        print('Done creating recipe')
        return new_recipe
