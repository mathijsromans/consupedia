from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
from .amount import ProductAmount
import re


class Ingredient(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name

    def alt_names(self):
        result = [self.name]
        words = self.name.split(" ")
        if len(words) > 1:
            result.append(" ".join(reversed(words)).replace(",", ""))  # "tijm, gedroogd" -> "gedroogd tijm"
        return result


class Score(models.Model):
    environment = models.IntegerField(null=True)
    social = models.IntegerField(null=True)
    animals = models.IntegerField(null=True)
    personal_health = models.IntegerField(null=True)


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


class Product(models.Model):
    CURRENT_VERSION = 1
    name = models.CharField(max_length=256, null=True)  # name according to Questionmark
    questionmark_id = models.IntegerField(default=0)
    brand = models.ForeignKey(Brand, null=True)
    ean_code = models.CharField(max_length=25, null=True)
    prices = models.ManyToManyField(Shop, through='ProductPrice')
    quantity = models.IntegerField(default=0)
    unit = models.CharField(max_length=5, choices=ProductAmount.UNIT_CHOICES, default=ProductAmount.NO_UNIT)
    ingredient = models.ForeignKey(Ingredient, null=True)
    scores = models.OneToOneField(Score, null=True)
    thumb_url = models.CharField(max_length=256, null=True)
    version = models.IntegerField(default=CURRENT_VERSION)
    product_score = 0
    product_score_details = ''

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
    user = models.OneToOneField(User, unique=True)
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

    def __str__(self):
        return 'Preferences of ' + self.user.username


class Rating(models.Model):
    user = models.ForeignKey(User, null=False)
    product = models.ForeignKey(Product, null=False)
    rating = models.IntegerField(null=False)

    class Meta:
        unique_together = (('user', 'product'),)


class Recipe(models.Model):
    name = models.CharField(max_length=256)
    author_if_user = models.ForeignKey(User, null=True, blank=True)
    source_if_not_user = models.CharField(max_length=256)
    number_persons = models.IntegerField(default=0)
    preparation_time_in_min = models.IntegerField(default=0)
    preparation = models.TextField()

    #otal_price_weight = calculateTotalPriceWeight(self)
    #otal_environment_weight = calculateTotalEnvironmentWeight(self)
    #otal_social_weight = calculateTotalSocialWeight(self)
    #total_animals_weight = calculateTotalAnimalsWeight(self)
    #total_personal_health_weight = calculateTotalPersonalHealthWeight(self)

    def __str__(self):
        return 'Recept ' + self.name

    def calculateTotalPriceWeight(self):
        return 0.5

    def calculateTotalEnvironmentWeight(self):
        return 0.5

    def calculateTotalSocialWeight(self):
        return 0.5

    def calculateTotalAnimalsWeight(self):
        return 0.5

    def calculateTotalPersonalHealthWeight(self):
        return 0.5

    def calcualteTotalScore(self, user_preference):
        return 0.6


from .algorithms import recommended_products

class RecipeItem(models.Model):
    quantity = models.IntegerField()
    unit = models.CharField(max_length=5, choices=ProductAmount.UNIT_CHOICES, default=ProductAmount.NO_UNIT)
    ingredient = models.ForeignKey(Ingredient)
    recipe = models.ForeignKey(Recipe)

    def get_amount(self):
        return ProductAmount(quantity=self.quantity, unit=self.unit)

    def price(self, user_preference):
        product_list = recommended_products(self.ingredient, user_preference)
        price = None
        if product_list:
            product = product_list[0]
            price = product.price.price * ( self.get_amount() / product.get_amount() )
        return price

    def price_str(self, user_preference):
        price = self.price(user_preference)
        if not price:
            return '?'
        return '€ {:03.2f}'.format(price/100.0)

    def __str__(self):
        return str(self.quantity) + ' ' + str(self.unit) + ' ' + str(self.ingredient)

class ProductPrice(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=256)  # name according to shop
    price = models.IntegerField()
    datetime_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '€ {:03.2f}'.format(self.price/100.0) + ' bij ' + str(self.shop)

