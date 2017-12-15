import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from product.productservice import RecipeService
from api import allerhande_scraper

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('url', nargs='+', type=str)

    def handle(self, *args, **options):
        url = options['url'][0]
        recipe_ids = allerhande_scraper.get_recipe_ids_from_page(url)
        for recipe_id in recipe_ids:
            RecipeService.create_recipe_from_id(recipe_id)
