from django.test import TestCase

from questionmark import api
from questionmark import allerhande_scraper


class TestQuestionApi(TestCase):

    def test_asserts(self):
        api.search_product('pindakaas')


class TestAllerHandeScraper(TestCase):
    recipe_id = 'R-R399568'

    def test_get_recipe_page_html(self):
        content, url = allerhande_scraper.get_recipe_page_html(self.recipe_id)

    def test_get_preparation_time(self):
        content, url = allerhande_scraper.get_recipe_page_html(self.recipe_id)
        preparation_time_in_min = allerhande_scraper.get_preparation_time_min(content)
        self.assertEqual(preparation_time_in_min, 45)

    def test_get_number_persons(self):
        content, url = allerhande_scraper.get_recipe_page_html(self.recipe_id)
        number_persons = allerhande_scraper.get_number_persons(content)
        self.assertEqual(number_persons, 10)
        content, url = allerhande_scraper.get_recipe_page_html('R-R543138')
        number_persons = allerhande_scraper.get_number_persons(content)
        self.assertEqual(number_persons, 4)

    def test_get_recipe_ingredient(self):
        content, url = allerhande_scraper.get_recipe_page_html(self.recipe_id)
        ingredients = allerhande_scraper.get_recipe_ingredients(content)
        self.assertEqual(ingredients[0][0], 4)
        self.assertEqual(ingredients[0][1], '')
        self.assertEqual(ingredients[0][2], 'ui')
        self.assertEqual(ingredients[-1][0], 1)
        self.assertEqual(ingredients[-1][1], 'kg')
        self.assertEqual(ingredients[-1][2], 'half-om-halfgehakt')

    def test_get_recipe(self):
        recipe = allerhande_scraper.get_recipe(self.recipe_id)
        self.assertEqual(recipe['url'], 'https://www.ah.nl/allerhande/recept/R-R399568')
        self.assertEqual(len(recipe['ingredients']), 9)
        self.assertEqual(recipe['preparation_time_in_min'], 45)
        self.assertEqual(recipe['number_persons'], 10)

    def test_get_name(self):
        content, url = allerhande_scraper.get_recipe_page_html(self.recipe_id)
        name = allerhande_scraper.get_name(content)
        self.assertEqual(name, 'Tante Greets spaghetti bolognese')
