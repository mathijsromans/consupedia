from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from api import questionmark, jumbo, ah, allerhande_scraper
from product.models import Product, Food, RecipeItem, Recipe, ProductPrice, Shop
from . import mappers
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
    def search_products(search_query):
        return Product.objects.filter(name__icontains=search_query)

    @staticmethod
    @transaction.atomic
    def update_products(food):
        logger.info('BEGIN: Updating products for food: ' + str(food))
        start = time.time()
        qm_entries = questionmark.search_product(food.name)
        logger.info('{}: Found {} questionmark entries'.format(time.time() - start, len(qm_entries)))

        jumbo_results = jumbo.search_product(food.name)
        logger.info('{}: Found {} jumbo entries'.format(time.time() - start, len(jumbo_results)))

        ah_results = ah.search_product(food.name)
        logger.info('{}: Found {} ah entries'.format(time.time() - start, len(ah_results)))

        unused = set(jumbo_results + ah_results)

        jumbo_shop, created = Shop.objects.get_or_create(name='Jumbo')
        ah_shop, created = Shop.objects.get_or_create(name='AH')

        product_ids = []
        for qm_entry in qm_entries:
            # logger.info('@1 ' + str(time.time() - start) + ': ' + product_dict['name'])
            product, created = Product.objects.get_or_create(name=qm_entry.name, questionmark_id=qm_entry.id, food=food)
            product = mappers.map_qm_to_product(product, qm_entry)
            ProductService.enrich_product_data(product, jumbo_results, jumbo_shop, unused)
            ProductService.enrich_product_data(product, ah_results, ah_shop, unused)
            product_ids.append(product.id)
            if not product.prices.exists():
                product.delete()

        for u in unused:
            logger.info('Unused result: {}'.format(u))

        logger.info('{}: Done')

        return Product.objects.filter(id__in=product_ids)

    @staticmethod
    def get_or_create_unknown_food():
        food, created = Food.objects.get_or_create(name='Unknown food')
        if created:
            Product.objects.get_or_create(name='Unknown product', food=food)
        return food

    @staticmethod
    def enrich_product_data(product, retailer_results, shop, unused):
        logger.info('SEARCHING FOR ' + product.name + ' (van ' + str(product.brand) + ') -> ' + product.get_full_name())
        for retailer_result in retailer_results:
            logger.info('CHECKING ' + str(retailer_result))
            if ProductService.match(retailer_result, product):
                logging.info('FOUND!!! ' + str(retailer_result))
                unused.discard(retailer_result)
                pp, created = ProductPrice.objects.update_or_create(
                    product=product, shop=shop, defaults={'price': retailer_result.price,
                                                          'product_name': retailer_result.name})
                pp.save()

    @staticmethod
    def match(retailer_result, product):
        retailer_size = ProductAmount.from_str(retailer_result.size)
        logger.info('Comparing amount {} -> {} == {}'.format(retailer_result.size, retailer_size, product.get_amount()))
        if retailer_size != product.get_amount():
            return False

        retailer_name = retailer_result.name
        size_sub = ProductAmount.extract_size_substring(retailer_name)
        if size_sub:
            retailer_name = retailer_name.replace(size_sub, '')
        name = product.get_full_name()

        if retailer_name == name:
            logger.info('Correct name')
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

        logger.info('Comparing {} == {}'.format(retailer_name.lower(), name.lower()))
        if retailer_name.lower() == name.lower():
            return True

        brands = ['Hero', 'Jumbo', 'AH']
        for brand in brands:
            retailer_name = retailer_name.replace(brand, '').strip()

        logger.info('Comparing {} == {}'.format(retailer_name, name))

        if retailer_name == name:
            return True
        return False

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
    def create_recipe_from_ah_id(recipe_id, provides, quantity, user):
        recipe = allerhande_scraper.get_recipe(recipe_id)
        return RecipeService.create_recipe(
            name=recipe['name'],
            provides=provides,
            quantity=quantity,
            user=user,
            source_if_not_user=recipe['url'],
            number_persons=recipe['number_persons'],
            preparation_time_in_min=recipe['preparation_time_in_min'],
            preparation='',
            recipe_items=recipe['recipe_items'],
            picture_url=recipe['picture_url']
        )

    @staticmethod
    def create_recipe(name,
                      provides,
                      quantity,
                      user,
                      source_if_not_user,
                      number_persons,
                      preparation_time_in_min,
                      preparation,
                      recipe_items,
                      picture_url):
        if Recipe.objects.filter(name=name).first():
            # recipe already exists
            return Recipe.objects.filter(name=name).first(), None

        logger.info('BEGIN: Creating recipe with recipe items: ' + str(recipe_items))
        start = time.time()

        new_recipe = Recipe.objects.create(name=name,
                                           provides=provides,
                                           quantity=quantity,
                                           user=user,
                                           source_if_not_user=source_if_not_user,
                                           number_persons=number_persons,
                                           preparation_time_in_min=preparation_time_in_min,
                                           preparation=preparation,
                                           picture_url=picture_url)

        foods_created = []
        for recipe_item in recipe_items:
            if len(recipe_item) != 3:
                continue
            recipe_item_quantity = recipe_item[0]
            recipe_item_unit = recipe_item[1]
            recipe_item_food = recipe_item[2]
            if recipe_item_food == 'water' or recipe_item_food == 'kraanwater':
                continue
            food, created = Food.objects.get_or_create(name=recipe_item_food)
            if created:
                foods_created.append(food.id)
            ProductService().update_products(food)
            quantity, unit = ProductAmount.get_quantity_and_unit(recipe_item_quantity, recipe_item_unit)
            RecipeItem.objects.create(quantity=quantity, food=food, recipe=new_recipe)
        
        end = time.time()
        logger.info('END: (time: ' + str(end - start) + ') Done creating recipe ' + str(new_recipe))
        
        return new_recipe, foods_created
