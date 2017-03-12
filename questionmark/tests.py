from django.test import TestCase

from questionmark import api
from questionmark import allerhande_scraper


class TestQuestionApi(TestCase):

    def test_asserts(self):
        api.search_product('pindakaas')


class TestAllerHandeScraper(TestCase):
    recipe_id = 'R-R399568'

    def test_get_recipe(self):
        content, url = allerhande_scraper.get_recipe_page_html(self.recipe_id)

    def test_get_preparation_time(self):
        content, url = allerhande_scraper.get_recipe_page_html(self.recipe_id)
        preparation_time_in_min = allerhande_scraper.get_preparation_time_min(content)
        self.assertEqual(preparation_time_in_min, 45)

    def test_get_recipe_ingredient(self):
        content, url = allerhande_scraper.get_recipe_page_html(self.recipe_id)
        ingredients = allerhande_scraper.get_recipe_ingredients(content)
        self.assertEqual(ingredients[0]['name'], 'ui')
        self.assertEqual(ingredients[0]['unit'], '')
        self.assertEqual(ingredients[0]['quantity'], 4)
        self.assertEqual(ingredients[-1]['name'], 'half-om-halfgehakt')
        self.assertEqual(ingredients[-1]['unit'], 'kg')
        self.assertEqual(ingredients[-1]['quantity'], 1)
