from django.test import TestCase

from api import allerhande_scraper

from .productservice import RecipeService
from .amount import ProductAmount


class TestCreateRecipe(TestCase):
    recipe_id = 'R-R399568'

    def test_create_recipe(self):
        recipe = allerhande_scraper.get_recipe(self.recipe_id)
        recipe_new = RecipeService.create_recipe(
            name=recipe['name'],
            author_if_user=None,
            source_if_not_user=recipe['url'],
            number_persons=recipe['number_persons'],
            preparation_time_in_min=recipe['preparation_time_in_min'],
            preparation='',
            ingredient_input=recipe['ingredients']

        )
        print(recipe_new)


class TestAmount(TestCase):
    recipe_id = 'R-R399568'

    def test_translate(self):
        self.assertEqual(ProductAmount.get_quantity_and_unit(200, 'g'), (200, 'g'))
        self.assertEqual(ProductAmount.get_quantity_and_unit(200, 'gr'), (200, 'g'))
        self.assertEqual(ProductAmount.get_quantity_and_unit(200, 'gram'), (200, 'g'))
        self.assertEqual(ProductAmount.get_quantity_and_unit(0.2, 'kg'), (200, 'g'))

        self.assertEqual(ProductAmount.get_quantity_and_unit(200, 'ml'), (200, 'ml'))
        self.assertEqual(ProductAmount.get_quantity_and_unit(20, 'cl'), (200, 'ml'))
        self.assertEqual(ProductAmount.get_quantity_and_unit(0.2, 'l'), (200, 'ml'))
        self.assertEqual(ProductAmount.get_quantity_and_unit(0.2, 'L'), (200, 'ml'))
        self.assertEqual(ProductAmount.get_quantity_and_unit(0.2, 'liter'), (200, 'ml'))
