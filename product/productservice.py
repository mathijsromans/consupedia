from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from questionmark import api, jumbo, ah
from product.models import Product, Category, Ingredient, Recipe, ProductPrice, Shop
from .mappers import QuestionmarkMapper
from .amount import ProductAmount
from questionmark import allerhande_scraper
import re
import logging
import time
import difflib

logger = logging.getLogger(__name__)


class ProductService:

    @staticmethod
    def get_all_products(search_query):
        if search_query:
            return ProductService.update_products(search_query)
        return Product.objects.all()

    @staticmethod
    @transaction.atomic
    def update_products(search_name):
        logger.info('BEGIN')
        start = time.time()
        qm_mapper = QuestionmarkMapper()

        products_dict = api.search_product(search_name)
        logger.info('@a: ' + str(time.time() - start))
        jumbo_results = jumbo.search_product(search_name)
        logger.info('@b: ' + str(time.time() - start))
        ah_results = ah.search_product(search_name)
        logger.info('@c: ' + str(time.time() - start))
        jumbo_shop, created = Shop.objects.get_or_create(name='Jumbo')
        logger.info('@d: ' + str(time.time() - start))
        ah_shop, created = Shop.objects.get_or_create(name='AH')

        product_ids = []
        for product_dict in products_dict['products']:
            logger.info('@1 ' + str(time.time() - start) + ': ' + product_dict['name'])
            product, created = Product.objects.get_or_create(name=product_dict['name'], questionmark_id=product_dict['id'])
            product = qm_mapper.map_to_product(product, product_dict)
            ProductService.enrich_product_data(product, jumbo_results, jumbo_shop)
            ProductService.enrich_product_data(product, ah_results, ah_shop)
            product_ids.append(product.id)
        end = time.time()
        logger.info('END - time: ' + str(end - start))

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
        # print ('SEARCHING FOR ' + product.name + ' (van ' + str(product.brand) + ') -> ' + product.get_full_name())
        for retailer_result in retailer_results:
            # print ('CHECKING ' + str(retailer_result))
            if ProductService.match(retailer_result, product):
                # print('FOUND!!! ' + str(retailer_result))
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
        retailer_name = retailer_name.replace('\'', '')
        # print('RETAILER_NAME AFTER: ' + retailer_name)

        name = re.sub('\(.*\)', '' , name)
        name = name.replace(' ', '')
        name = name.replace('-', '')
        name = name.replace('\'', '')

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
                    break
        if product_dict['brand']:
            if product_dict['brand']['name'] == 'Jumbo':
                contains = True
        return contains


class RecipeService():

    @staticmethod
    def create_recipe_from_id(recipe_id):
        recipe = allerhande_scraper.get_recipe(recipe_id)
        return RecipeService.create_recipe(
            name=recipe['name'],
            author_if_user=None,
            source_if_not_user=recipe['url'],
            number_persons=recipe['number_persons'],
            preparation_time_in_min=recipe['preparation_time_in_min'],
            preparation='',
            ingredient_input=recipe['ingredients']
        )

    @staticmethod
    def create_recipe(name,
                      author_if_user,
                      source_if_not_user,
                      number_persons,
                      preparation_time_in_min,
                      preparation,
                      ingredient_input):
        logger.info('BEGIN')
        start = time.time()
        test_ingredients = [
            [2, '-', 'uien'],
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
        new_recipe = Recipe.objects.create(name=name,
                                           author_if_user=author_if_user,
                                           source_if_not_user = source_if_not_user,
                                           number_persons = number_persons,
                                           preparation_time_in_min = preparation_time_in_min,
                                           preparation = preparation)
        for ing in ingredient_input:
            if len(ing) == 3:
                ProductService().get_all_products(ing[2])
        all_categories = Category.objects.all()
        all_category_names = [name for c in all_categories for name in c.alt_names()]
        unknown_category = ProductService.get_or_create_unknown_category()
        for ing in ingredient_input:
            if len(ing) != 3:
                continue
            # print('searching ' + ing[2])
            try:
                best_category_name = difflib.get_close_matches(ing[2], all_category_names, 1, 0.1)[0]
                category = next(c for c in all_categories if best_category_name in c.alt_names())
            except StopIteration:
                category = unknown_category
            # print('found category ' + str(category))
            quantity, unit = ProductAmount.get_quantity_and_unit( ing[0], ing[1])
            Ingredient.objects.create(quantity=quantity, unit=unit, category=category, recipe = new_recipe)
        print('Done creating recipe ' + str(new_recipe))
        end = time.time()
        logger.info('END - time: ' + str(end - start))
        return new_recipe
