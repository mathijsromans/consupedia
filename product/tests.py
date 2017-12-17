from django.test import TestCase

from api import allerhande_scraper

from .productservice import RecipeService
from .amount import ProductAmount


class TestCreateRecipe(TestCase):
    def test_water(self):
        recipe, ingredients_created = RecipeService.create_recipe_from_ah_id('R-R1189786')
        recipe_items = recipe.recipeitem_set.all()
        for ri in recipe_items:
            self.assertNotEqual(ri.ingredient.name, 'water')
            self.assertNotEqual(ri.ingredient.name, 'kraanwater')
        self.assertEqual(len(recipe_items), 7)

class TestAmount(TestCase):
    recipe_id = 'R-R399568'

    def test_translate(self):
        self.assertEqual(ProductAmount.get_quantity_and_unit(200, 'g'), (200, 'g'))
        self.assertEqual(ProductAmount.get_quantity_and_unit(200, 'gr'), (200, 'g'))
        self.assertEqual(ProductAmount.get_quantity_and_unit(200, 'gram'), (200, 'g'))
        self.assertEqual(ProductAmount.get_quantity_and_unit(0.2, 'kg'), (200, 'g'))

        self.assertEqual(ProductAmount.get_quantity_and_unit(0.5, 'pond'),(250, 'g'))
        self.assertEqual(ProductAmount.get_quantity_and_unit(1, 'pondje'),(500, 'g'))        
        self.assertEqual(ProductAmount.get_quantity_and_unit(0.2, 'ons'), (20, 'g'))
        self.assertEqual(ProductAmount.get_quantity_and_unit(1.0, 'onsje'), (100, 'g'))
        self.assertEqual(ProductAmount.get_quantity_and_unit(0.5, 'snee'), (40, 'g'))
        self.assertEqual(ProductAmount.get_quantity_and_unit(1.0, 'sneetje'), (80, 'g'))
        self.assertEqual(ProductAmount.get_quantity_and_unit(1.0, 'blok'), (10, 'g'))
        self.assertEqual(ProductAmount.get_quantity_and_unit(0.5, 'blokje'), (5, 'g'))
        self.assertEqual(ProductAmount.get_quantity_and_unit(1, 'blik'), (400, 'g'))
        self.assertEqual(ProductAmount.get_quantity_and_unit(1, 'blikje'), (100, 'g'))

        self.assertEqual(ProductAmount.get_quantity_and_unit(200, 'ml'), (200, 'ml'))
        self.assertEqual(ProductAmount.get_quantity_and_unit(20, 'cl'), (200, 'ml'))
        self.assertEqual(ProductAmount.get_quantity_and_unit(0.2, 'l'), (200, 'ml'))
        self.assertEqual(ProductAmount.get_quantity_and_unit(0.2, 'L'), (200, 'ml'))
        self.assertEqual(ProductAmount.get_quantity_and_unit(0.2, 'liter'), (200, 'ml'))
