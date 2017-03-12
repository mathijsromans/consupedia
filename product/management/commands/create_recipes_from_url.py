import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from product.productservice import RecipeService
from questionmark import allerhande_scraper

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('url', nargs='+', type=str)

    def handle(self, *args, **options):
        url = options['url'][0]
        recipe_ids = allerhande_scraper.get_recipe_ids_from_page(url)
        for id in recipe_ids:
            self.create_recipe(id)

    @staticmethod
    @transaction.atomic
    def create_recipe(recipe_id):
        try:
            recipe = allerhande_scraper.get_recipe(recipe_id)
            RecipeService.create_recipe(
                name=recipe['name'],
                author_if_user=None,
                source_if_not_user=recipe['url'],
                number_persons=recipe['number_persons'],
                preparation_time_in_min=recipe['preparation_time_in_min'],
                preparation='',
                ingredient_input=recipe['ingredients']
            )
        except Exception as error:
            logger.exception(error)
            logger.error('error for recipe id: ' + str(recipe_id) + ', skip recipe!')

