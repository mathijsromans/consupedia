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

    def __str__(self):
        return 'Recept ' + self.name

    def recommended_scores(self, up):
        result = []
        for recipe_item in self.recipeitem_set.all():
            product = recipe_item.recommended_product(up)
            if product and product.scores:
                result.append(product.scores)
        return result

    def calculateTotalPriceWeight(self, up):
        total = 0
        for recipe_item in self.recipeitem_set.all():
            total += recipe_item.price_estimate(up)
        return total

    def calculateTotalEnvironmentWeight(self, up):
        sum = 0
        n = 1
        rec_scores = self.recommended_scores(up)
        for scores in rec_scores:
            if scores.environment:
                sum += scores.environment
                n += 1
        return sum / n

    def calculateTotalSocialWeight(self, up):
        sum = 0
        n = 1
        rec_scores = self.recommended_scores(up)
        for scores in rec_scores:
            if scores.social:
                sum += scores.social
                n += 1
        return sum / n

    def calculateTotalAnimalsWeight(self, up):
        sum = 0
        n = 1
        rec_scores = self.recommended_scores(up)
        for scores in rec_scores:
            if scores.animals:
                sum += scores.animals
                n += 1
        return sum / n

    def calculateTotalPersonalHealthWeight(self, up):
        sum = 0
        n = 1
        rec_scores = self.recommended_scores(up)
        for scores in rec_scores:
            if scores.personal_health:
                sum += scores.personal_health
                n += 1
        return sum / n

    def calcualteTotalScore(self, up):
        total_price_weight = self.calculateTotalPriceWeight(up) * up.price_weight
        total_environment_weight = self.calculateTotalEnvironmentWeight(up) * up.environment_weight
        total_social_weight = self.calculateTotalSocialWeight(up) * up.social_weight
        total_animals_weight = self.calculateTotalAnimalsWeight(up) * up.animals_weight
        total_personal_health_weight = self.calculateTotalPersonalHealthWeight(up) * up.personal_health_weight
        return total_price_weight + \
            total_environment_weight + \
            total_social_weight + \
            total_animals_weight + \
            total_personal_health_weight


from .algorithms import recommended_products

class RecipeItem(models.Model):
    quantity = models.IntegerField()
    unit = models.CharField(max_length=5, choices=ProductAmount.UNIT_CHOICES, default=ProductAmount.NO_UNIT)
    ingredient = models.ForeignKey(Ingredient)
    recipe = models.ForeignKey(Recipe)

    def get_amount(self):
        return ProductAmount(quantity=self.quantity, unit=self.unit)

    def recommended_product(self, user_preference):
        product_list = recommended_products(self.ingredient, user_preference)
        if product_list:
            return product_list[0]
        return None

    def price(self, user_preference):
        product = self.recommended_product(user_preference)
        if product:
            return product.price.price * ( self.get_amount() / product.get_amount() )
        return None

    def price_estimate(self, user_preference):
        price = self.price(user_preference)
        if price:
            return price
        return 0.5  # should be error, really

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

