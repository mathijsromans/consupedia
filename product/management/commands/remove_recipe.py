import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from product.productservice import Recipe
from questionmark import allerhande_scraper

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('recipe_id', nargs='?', default='R-R399568', type=str)

    def handle(self, *args, **options):
        self.remove_recipe(options['recipe_id'])

    @staticmethod
    @transaction.atomic
    def remove_recipe(recipe_id):
        try:
            recipe_data = allerhande_scraper.get_recipe(recipe_id)
            recipe = Recipe.objects.get(source_if_not_user=recipe_data['url'])
            recipe.delete()
        except Exception as error:
            logger.exception(error)
            logger.error('error for recipe id: ' + str(recipe_id) + ', skip recipe!')

