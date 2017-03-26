from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from questionmark import api, jumbo, ah
from .models import Product, Category, Ingredient, Recipe, ProductPrice, Shop
from .mappers import QuestionmarkMapper
from .amount import ProductAmount
import re
import difflib

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
        jumbo_shop, created = Shop.objects.get_or_create(name='Jumbo')
        ah_shop, created = Shop.objects.get_or_create(name='AH')

        product_ids = []
        for product_dict in products_dict['products']:
            product, created = Product.objects.get_or_create(name=product_dict['name'])
            product = qm_mapper.map_to_product(product, product_dict)
            ProductService.enrich_product_data(product, jumbo_results, jumbo_shop)
            ProductService.enrich_product_data(product, ah_results, ah_shop)
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
    def enrich_product_data(product, retailer_results, shop):
        # print ('SEARCHING FOR ' + product.name + ' -> ' + product.get_full_name())
        for retailer_result in retailer_results:
            # print ('CHECKING ' + str(retailer_result))
            if ProductService.match(retailer_result, product):
                # print('FOUND!!! ' + str(retailer_result))
                print(shop)
                price = int(retailer_result['price'])
                product_name = retailer_result['name']
                try:
                    pp = ProductPrice.objects.get(product=product, shop=shop)
                    pp.price = price
                    pp.product_name = product_name
                    pp.save()
                except ObjectDoesNotExist:
                    ProductPrice.objects.create(product=product, shop=shop, price=price, product_name=product_name)

    @staticmethod
    def match(retailer_result, product):
        if ProductAmount.from_str(retailer_result['size']) != product.get_amount():
            return False

        retailer_name = retailer_result['name']
        size_sub = ProductAmount.extract_size_substring(retailer_name)
        if size_sub:
            retailer_name = retailer_name.replace(size_sub, '')
        name = product.get_full_name()

        if retailer_name == name:
            return True

        # print('RETAILER_NAME BEFORE: ' + retailer_name)
        retailer_name = re.sub(' [0-9]+g', '', retailer_name)
        retailer_name = retailer_name.replace('\xad', '')
        retailer_name = retailer_name.replace(' ', '')
        retailer_name = retailer_name.replace('-', '')
        # print('RETAILER_NAME AFTER: ' + retailer_name)

        name = re.sub('\(.*\)', '' , name)
        name = name.replace(' ', '')
        name = name.replace('-', '')

        if retailer_name.lower() == name.lower():
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
            if len(ing) == 3:
                ProductService().get_all_products(ing[2])
        all_categories = Category.objects.all()
        all_category_names = []
        for c in all_categories:
            all_category_names.append(c.name)
        unknown_category = ProductService.get_or_create_unknown_category()
        for ing in ingredient_input:
            if len(ing) == 3:
                quantity = 0
                unit = ProductAmount.NO_UNIT
                # print('searching ' + ing[2])
                best_category_name = difflib.get_close_matches(ing[2], all_category_names, 1, 0.1)
                # print ('found ' + str(best_category_name))
                category = all_categories[all_category_names.index(best_category_name[0])] if best_category_name else unknown_category
                quantity, unit = ProductAmount.get_quantity_and_unit( ing[0], ing[1])
                Ingredient.objects.create(quantity=quantity, unit=unit, category=category, recipe = new_recipe)
        print('Done creating recipe')
        return new_recipe
