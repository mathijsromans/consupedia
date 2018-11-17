import logging
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
from django.core.validators import MinValueValidator
from .amount import ProductAmount
from collections import namedtuple
import re
import copy

logger = logging.getLogger(__name__)


class Price:
    def __init__(self, cents):
        self.cents = cents

    def __mul__(self, other):
        return Price(self.cents * other)

    def __str__(self):
        if self.cents:
            return '€ {:03.2f}'.format(self.cents/100.0)
        return '€ ?'


class Score:
    def __init__(self, user_pref):
        self.user_pref = user_pref
        self._scores = {}

    def __lt__(self, other):
        return self.total() < other.total()

    def scale(self, scalar):
        for key, value in self._scores.items():
            self._scores[key] = scalar * value

    def scaled(self, scalar):
        result = copy.deepcopy(self)
        result.scale(scalar)
        return result

    def add(self, other):
        logger.info('{}'.format(self))
        for key, value in other._scores.items():
            self.add_score(key, value)

    def add_score(self, key, value):
        if not key or not value:
            return
        if key in self._scores:
            self._scores[key] += value
        else:
            self._scores[key] = value

    def price(self):
        return Price(self._scores.get('price'))

    def total(self):
        result = 0
        user_pref_dict = self.user_pref.get_dict()
        for key, value in self._scores.items():
            user_pref_value = user_pref_dict.get(key, 1.0)
            if user_pref_dict and value is not None:
                result += value * user_pref_value
        return result

    def __str__(self):
        result = ''
        user_pref_dict = self.user_pref.get_dict()
        for key, value in self._scores.items():
            user_pref_value = user_pref_dict.get(key, 1.0)
            if user_pref_dict and value is not None:
                partial = value * user_pref_value
                result += '[{}: {:.2f} -> {:.2f}] '.format(key, value, partial)
        result += '-> {:.2f}'.format(self.total())
        return result


class ScoreCreator(models.Model):
    name = models.CharField(max_length=255)
    production_in_ton_per_ha = models.FloatField(default=5)
    killed_animal_iq_points = models.FloatField(default=0)
    sources = models.TextField(blank=True)
    user = models.ForeignKey(User, null=False)

    def append_score(self, score, weight):
        m2_per_g = 0.01
        days_per_year = 365
        score.add_score('land_use_m2', weight*days_per_year*m2_per_g/self.production_in_ton_per_ha)
        score.add_score('animal_harm', weight*self.killed_animal_iq_points)

    def __str__(self):
        return self.name


class Food(models.Model):
    """ Describes anything that can be eaten with various degrees of specificity

    Has a unit but quantity is always 1

    Examples: 1 sandwich
              1 g of brown rice
              1 g of vegetables
              1 ml of soft drink
              1 g of salt consisting of 33.3% NaCl, 66% KCl,  50mg/kg (KI)
    """

    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=5, choices=ProductAmount.UNIT_CHOICES, default=ProductAmount.NO_UNIT)
    score_creator = models.ForeignKey(ScoreCreator, null=True)
    equiv_weight = models.FloatField(null=True, blank=True)

    def get_score_creator(self):
        if not self.score_creator:
            self.score_creator, created = ScoreCreator.objects.get_or_create(name='default')
        return self.score_creator

    def recommended_product_and_score(self, user_preference):
        products_and_scores = self.recommended_products_and_scores(user_preference)
        if products_and_scores:
            return products_and_scores[0]
        return None

    def weight(self):
        if self.equiv_weight:
            return self.equiv_weight
        return 1

    def recommended_products_and_scores(self, user_preference):
        product_list = self.product_set.all()
        products_and_scores = []
        sc = self.get_score_creator()
        for product in product_list:
            score = product.score(user_preference)
            sc.append_score(score, self.weight())
            products_and_scores.append((product, score))
        products_and_scores.sort(key=lambda x: x[1].total())
        return products_and_scores

    def recommended_recipe_and_score(self, user_preference):
        recipe_list = self.recommended_recipes_and_scores(user_preference)
        if recipe_list:
            return recipe_list[0]
        return None

    def recommended_recipes_and_scores(self, user_preference):
        logger.info('recommended_recipes_and_scores for {}'.format(self))
        conversions = self.conversion_set.all()
        for c in conversions:
            logger.info('Conversion {}'.format(c))
        recipes = Recipe.objects.filter(provides=self)
        for r in recipes:
            logger.info('Recipe {}'.format(r))
        recipes_and_scores = [(recipe, recipe.score(user_preference)) for recipe in recipes]
        recipes_and_scores.sort(key=lambda x: x[1].total())
        return recipes_and_scores

    def recommended_product_recipe_score(self, user_preference):
        Recommendation = namedtuple('Recommendation', ['product', 'recipe', 'score'])
        product_and_score = self.recommended_product_and_score(user_preference)
        recipe_and_score = self.recommended_recipe_and_score(user_preference)
        if not recipe_and_score and not product_and_score:
            return Recommendation(None, None, None)
        if not recipe_and_score or (product_and_score and product_and_score[1] < recipe_and_score[1]):
            return Recommendation(product_and_score[0], None, product_and_score[1])
        return Recommendation(None, recipe_and_score[0], recipe_and_score[1])

    def score(self, user_preference):
        s = self.recommended_product_recipe_score(user_preference).score
        if not s:
            s = Score(user_preference)
        return s

    def __str__(self):
        return self.name


class ProductScore(models.Model):
    environment = models.IntegerField(null=True)
    social = models.IntegerField(null=True)
    animals = models.IntegerField(null=True)
    personal_health = models.IntegerField(null=True)

    def score(self, userpref):
        result = Score(userpref)
        result.add_score('environment', self.environment)
        result.add_score('social', self.social)
        result.add_score('animals', self.animals)
        result.add_score('health', self.personal_health)
        return result


class Brand(models.Model):
    name = models.CharField(max_length=256)  # name according to Questionmark

    def simple_name(self):
        return self.name.replace('Biologisch van', '')

    def __str__(self):
        return self.name


class Shop(models.Model):
    name = models.CharField(max_length=80)

    def __str__(self):
        return self.name


class ScoreTheme(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return 'Theme: {}'.format(self.name)


class ProductUsage(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return 'Usage: {}'.format(self.name)


class Certificate(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=256)
    image_url = models.CharField(max_length=256)
    themes = models.ManyToManyField(ScoreTheme)

    def __str__(self):
        return 'Certificate: {}'.format(self.name)


class Product(models.Model):
    CURRENT_VERSION = 1
    name = models.CharField(max_length=256, null=True)  # name according to Questionmark
    questionmark_id = models.IntegerField(default=0)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True, blank=True)
    ean_code = models.CharField(max_length=25, null=True, blank=True)
    prices = models.ManyToManyField(Shop, through='ProductPrice')
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    unit = models.CharField(max_length=5, choices=ProductAmount.UNIT_CHOICES, default=ProductAmount.NO_UNIT)
    food = models.ForeignKey(Food, on_delete=models.CASCADE, null=False)
    scores = models.OneToOneField(ProductScore, on_delete=models.CASCADE, null=True)
    thumb_url = models.CharField(max_length=256, null=True)
    version = models.IntegerField(default=CURRENT_VERSION)
    energy_in_kj_per_100_g = models.FloatField(blank=True, null=True, default=None)
    protein_in_g_per_100_g = models.FloatField(blank=True, null=True, default=None)
    carbohydrates_in_g_per_100_g = models.FloatField(blank=True, null=True, default=None)
    sugar_in_g_per_100_g = models.FloatField(blank=True, null=True, default=None)
    fat_saturated_in_g_per_100_g = models.FloatField(blank=True, null=True, default=None)
    fat_total_in_g_per_100_g = models.FloatField(blank=True, null=True, default=None)
    salt_in_g_per_100_g = models.FloatField(blank=True, null=True, default=None)
    fiber_in_g_per_100_g = models.FloatField(blank=True, null=True, default=None)
    certificates = models.ManyToManyField(Certificate)
    usages = models.ManyToManyField(ProductUsage)

    def score(self, user_pref):
        s = Score(user_pref)
        if self.price:
            s.add_score('price', self.price.price)
        if self.scores:
            s.add(self.scores.score(user_pref))
        if self.quantity:
            s.scale(1.0/self.quantity)
        return s

    @property
    def price(self):
        min_pp = None
        for pp in self.productprice_set.all():
            if not min_pp or pp.price < min_pp.price:
                min_pp = pp
        return min_pp

    def get_full_name(self):
        full_name = self.name
        size = ProductAmount.extract_size_substring(self.name)
        if size:
            full_name = full_name.replace(size, '')
        if self.brand:
            simple_brand_name = self.brand.simple_name()
            if not self.name.startswith(simple_brand_name):
                full_name = simple_brand_name + ' ' + full_name
        full_name = re.sub('\(.*\)', '' , full_name)
        return full_name

    def amount_from_name(self):
        size = ProductAmount.extract_size_substring(self.name)
        if size:
            return ProductAmount.from_str(size)
        return None

    def set_rating(self, user, rating_value):
        ratings = Rating.objects.filter(product=self, user=user)
        if ratings.exists():
            rating = ratings[0]
            rating.rating = rating_value
            rating.save()
        else:
            Rating.objects.create(product=self, user=user, rating=rating_value)

    def get_rating(self, user):
        rating = Rating.objects.filter(product=self, user=user)
        return rating

    def get_average_rating(self):
        ratings = Rating.objects.filter(product=self).aggregate(Avg('rating'))
        return ratings['rating__avg']

    def set_amount(self, product_amount):
        self.quantity = product_amount.quantity
        self.unit = product_amount.unit

    def get_amount(self):
        return ProductAmount(quantity=self.quantity, unit=self.unit)

    def __str__(self):
        return self.name


class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    price_weight = models.IntegerField(default=50)
    environment_weight = models.IntegerField(default=50)
    social_weight = models.IntegerField(default=50)
    animals_weight = models.IntegerField(default=50)
    personal_health_weight = models.IntegerField(default=50)

    def get_rel_weights(self):
        #normaliseren van de gebruikersgewichten.
        #voorbeeld : 6,2,4,1 => 1,0.3333,0.66666,0.
        userweights = self.get_weights()
        maxval = max(userweights) or 1
        normalizedUserweights = []
        for weight in userweights:
            normalizedUserweights.append(float(weight / maxval))
        return normalizedUserweights

    def get_weights(self):
        return [self.price_weight, self.environment_weight, self.social_weight, self.animals_weight, self.personal_health_weight]

    def get_dict(self):
        return {
            'price': self.price_weight,
            'environment': self.environment_weight,
            'social': self.social_weight,
            'animals': self.animals_weight,
            'health': self.personal_health_weight,
        }

    def __str__(self):
        return 'Preferences of ' + self.user.username


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False)
    rating = models.IntegerField(null=False)

    class Meta:
        unique_together = (('user', 'product'),)


class Conversion(models.Model):
    provides = models.ForeignKey(Food, on_delete=models.CASCADE, null=False)


class Recipe(Conversion):
    name = models.CharField(max_length=256)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=2)
    quantity = models.IntegerField()
    source_if_not_user = models.CharField(max_length=256)
    number_persons = models.IntegerField(default=0)
    preparation_time_in_min = models.IntegerField(default=0)
    picture_url = models.CharField(max_length=256)
    preparation = models.TextField()

    def __str__(self):
        return 'Recept ' + self.name

    FQS = namedtuple('FQS', ['food', 'quantity', 'score'])

    def food_quantity_scores(self, userpreference):
        return [Recipe.FQS(recipe_item.food, recipe_item.quantity, recipe_item.score(userpreference)) for recipe_item in self.recipeitem_set.all()]

    def recursive_food_quantity_scores(self, userpreference):
        result = []
        for recipe_item in self.recipeitem_set.all():
            prs = recipe_item.food.recommended_product_recipe_score(userpreference)
            if prs.recipe:
                fqs_list = prs.recipe.recursive_food_quantity_scores(userpreference)
                scale = recipe_item.quantity / prs.recipe.quantity
                for fqs in fqs_list:
                    result.append(Recipe.FQS(fqs.food, fqs.quantity*scale, fqs.score.scaled(scale)))
            else:
                result.append(Recipe.FQS(recipe_item.food, recipe_item.quantity, recipe_item.score(userpreference)))
        return result

    def recursive_preparation(self, userpreference):
        result = ''
        for recipe_item in self.recipeitem_set.all():
            prs = recipe_item.food.recommended_product_recipe_score(userpreference)
            if prs.recipe:
                result += prs.recipe.recursive_preparation(userpreference) + ' '
        return result + self.preparation

    def score(self, user_pref):
        s = Score(user_pref)
        for recipe_item in self.recipeitem_set.all():
            s.add(recipe_item.score(user_pref))
        s.scale(1.0/self.quantity)
        return s


class RecipeItem(models.Model):
    quantity = models.IntegerField()
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def get_amount(self):
        return ProductAmount(quantity=self.quantity, unit=self.food.unit)

    def score(self, user_pref):
        score = self.food.score(user_pref)
        score.scale(self.quantity)
        return score

    @property
    def name(self):
        return str(self)

    def __str__(self):
        return str(self.quantity) + ' ' + str(self.food.unit) + ' ' + str(self.food)


class ProductPrice(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=256)  # name according to shop
    price = models.IntegerField()
    datetime_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(Price(self.price)) + ' bij ' + str(self.shop)

