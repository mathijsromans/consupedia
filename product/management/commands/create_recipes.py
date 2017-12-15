import logging
from django.core.management.base import BaseCommand

from product.productservice import RecipeService


logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('recipe_ids', nargs='+', default=['R-R399568', 'R-R543138', 'R-R1185720'], type=str)

    def handle(self, *args, **options):
        for recipe_id in options['recipe_ids']:
            RecipeService.create_recipe_from_id(recipe_id)

