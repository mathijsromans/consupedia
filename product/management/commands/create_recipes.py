import logging
from django.core.management.base import BaseCommand

from product.productservice import RecipeService
from questionmark import allerhande_scraper

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('recipe_ids', nargs='+', default=['R-R399568', 'R-R543138', 'R-R1185720'], type=str)

    def handle(self, *args, **options):
        for recipe_id in options['recipe_ids']:
            self.create_recipe(recipe_id)

    @staticmethod
    def create_recipe(recipe_id):
        try:
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
        except Exception as error:
            logger.exception(error)
            logger.error('error for recipe id: ' + str(recipe_id) + ', skip recipe!')

