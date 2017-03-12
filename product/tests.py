from django.test import TestCase

from questionmark import allerhande_scraper

from .productservice import RecipeService


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