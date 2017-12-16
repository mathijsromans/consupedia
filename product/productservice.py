from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from api import questionmark, jumbo, ah, allerhande_scraper
from product.models import Product, Ingredient, RecipeItem, Recipe, ProductPrice, Shop
from .mappers import QuestionmarkMapper
from .amount import ProductAmount
import re
import logging
import time
import difflib

logger = logging.getLogger(__name__)


class ProductService:
    @staticmethod
    def get_all_products():
        return Product.objects.all()

    @staticmethod
    def search_or_update_products(search_query):
        products_all = Product.objects.filter(name__icontains=search_query)
        if not products_all.exists():
            ingredient, created = Ingredient.objects.get_or_create(name=search_query)
            products_all = ProductService.update_products(ingredient)
        return products_all

    @staticmethod
    @transaction.atomic
    def update_products(ingredient):
        # logger.info('BEGIN: Updating products for ingredient: ' + str(ingredient))
        # start = time.time()
        qm_mapper = QuestionmarkMapper()

        products_dict = questionmark.search_product(ingredient.name)
        # logger.info('@a: ' + str(time.time() - start))
        jumbo_results = jumbo.search_product(ingredient.name)
        # logger.info('@b: ' + str(time.time() - start))
        ah_results = ah.search_product(ingredient.name)
        # logger.info('@c: ' + str(time.time() - start))
        jumbo_shop, created = Shop.objects.get_or_create(name='Jumbo')
        # logger.info('@d: ' + str(time.time() - start))
        ah_shop, created = Shop.objects.get_or_create(name='AH')

        product_ids = []
        for product_dict in products_dict['products']:
            if not product_dict['name'].lower().startswith(ingredient.name + ' '):
                continue  # Boterhamworst is not a type of boter
            # logger.info('@1 ' + str(time.time() - start) + ': ' + product_dict['name'])
            product, created = Product.objects.get_or_create(name=product_dict['name'], questionmark_id=product_dict['id'])
            product.ingredient = ingredient
            product = qm_mapper.map_to_product(product, product_dict)
            ProductService.enrich_product_data(product, jumbo_results, jumbo_shop)
            ProductService.enrich_product_data(product, ah_results, ah_shop)
            product_ids.append(product.id)
        
        # end = time.time()
        # logger.info('END - time: ' + str(end - start))

        return Product.objects.filter(id__in=product_ids)

    @staticmethod
    def get_or_create_unknown_ingredient():
        ingredient, created = Ingredient.objects.get_or_create(name='Unknown ingredient')
        if created:
            product, created = Product.objects.get_or_create(name='Unknown product')
            product.ingredient = ingredient
        return ingredient

    @staticmethod
    def enrich_product_data(product, retailer_results, shop):
        # print ('SEARCHING FOR ' + product.name + ' (van ' + str(product.brand) + ') -> ' + product.get_full_name())
        for retailer_result in retailer_results:
            # print ('CHECKING ' + str(retailer_result))
            if ProductService.match(retailer_result, product):
                logging.info('FOUND!!! ' + str(retailer_result))
                price = int(retailer_result['price'])
                product_name = retailer_result['name']
                try:
                    pp = ProductPrice.objects.get(product=product, shop=shop)
                    pp.price = price
                    pp.product_name = product_name
                    pp.save()
                except ObjectDoesNotExist:
                    logger.exception('Product should exist already, but was not found: ' + product.name)
                    ProductPrice.objects.create(product=product, shop=shop, price=price, product_name=product_name)

    @staticmethod
    def match(retailer_result, product):
        retailer_size = ProductAmount.from_str(retailer_result['size']);
        if retailer_size != product.get_amount():
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
    def create_recipe_from_ah_id(recipe_id):
        recipe = allerhande_scraper.get_recipe(recipe_id)
        return RecipeService.create_recipe(
            name=recipe['name'],
            author_if_user=None,
            source_if_not_user=recipe['url'],
            number_persons=recipe['number_persons'],
            preparation_time_in_min=recipe['preparation_time_in_min'],
            preparation='',
            recipe_items=recipe['recipe_items']
        )

    @staticmethod
    def create_recipe(name,
                      author_if_user,
                      source_if_not_user,
                      number_persons,
                      preparation_time_in_min,
                      preparation,
                      recipe_items):
        if Recipe.objects.filter(name=name).first():
            # recipe already exists
            return

        logger.info('BEGIN: Creating recipe with recipe items: ' + str(recipe_items))
        start = time.time()

        new_recipe = Recipe.objects.create(name=name,
                                           author_if_user=author_if_user,
                                           source_if_not_user = source_if_not_user,
                                           number_persons = number_persons,
                                           preparation_time_in_min = preparation_time_in_min,
                                           preparation = preparation)

        for recipe_item in recipe_items:
            if len(recipe_item) != 3:
                continue
            recipe_item_quantity = recipe_item[0]
            recipe_item_unit = recipe_item[1]
            recipe_item_ingredient = recipe_item[2]
            ingredient, created = Ingredient.objects.get_or_create(name=recipe_item_ingredient)
            ProductService().update_products(ingredient)
            quantity, unit = ProductAmount.get_quantity_and_unit( recipe_item_quantity, recipe_item_unit)
            RecipeItem.objects.create(quantity=quantity, unit=unit, ingredient=ingredient, recipe = new_recipe)
        
        end = time.time()
        logger.info('END: (time: ' + str(end - start) + ') Done creating recipe ' + str(new_recipe))
        
        return new_recipe
