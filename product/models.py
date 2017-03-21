from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
import re


class ProductAmount:
    NO_UNIT = '-'
    GRAM = 'g'
    ML = 'ml'
    EL = 'el'
    UNIT_CHOICES = (
        (NO_UNIT, 'st.'),
        (GRAM, 'g'),
        (ML, 'ml'),
        (EL, 'el')
    )

    def __init__(self, quantity, unit):
        self.quantity = quantity
        self.unit = unit

    @classmethod
    def from_str(cls, size):
        quantity = 0
        unit = ProductAmount.NO_UNIT

        size = size.replace(',', '.')
        numbers = re.findall(r'[-+]?\d*\.\d+|\d+', size)
        if numbers:
            nonnumbers = re.sub('[0-9\. ]', '', size)
            quantity, unit = ProductAmount.get_quantity_and_unit(float(numbers[0]), nonnumbers)
        return cls(quantity, unit)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        return str(self.quantity) + ' ' + self.unit

    @staticmethod
    def get_quantity_and_unit(quantity, unit_text):
        if unit_text == '-' or unit_text == 'blaadjes' or unit_text == 'stuks':
            return quantity, ProductAmount.NO_UNIT
        if unit_text == 'g' or unit_text == 'gr' or unit_text == 'gram':
            return quantity, ProductAmount.GRAM
        if unit_text == 'kg':
            return 1000*quantity, ProductAmount.GRAM
        if unit_text == 'ml':
            return quantity, ProductAmount.ML
        if unit_text == 'cl':
            return 10*quantity, ProductAmount.ML
        if unit_text == 'l' or unit_text == 'L' or unit_text == 'liter':
            return 1000*quantity, ProductAmount.ML
        if unit_text == 'el':
            return quantity, ProductAmount.EL
        print('UNKNOWN UNIT : ' + unit_text)
        return int(quantity), ProductAmount.NO_UNIT


class Category(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Score(models.Model):
    environment = models.IntegerField(null=True)
    social = models.IntegerField(null=True)
    animals = models.IntegerField(null=True)
    personal_health = models.IntegerField(null=True)

class Brand(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name

class Product(models.Model):
    CURRENT_VERSION = 1
    name = models.CharField(max_length=256, null=True)  # name according to Questionmark
    questionmark_id = models.IntegerField(default=0)
    brand = models.ForeignKey(Brand, null=True)
    ean_code = models.CharField(max_length=25, null=True)
    price = models.IntegerField(null=True)
    quantity = models.IntegerField(default=0)
    unit = models.CharField(max_length=5, choices=ProductAmount.UNIT_CHOICES, default=ProductAmount.NO_UNIT)
    category = models.ForeignKey(Category, null=True)
    scores = models.OneToOneField(Score, null=True)
    thumb_url = models.CharField(max_length=256, null=True)
    version = models.IntegerField(default=CURRENT_VERSION)
    product_score = 0
    product_score_details = ''

    def get_full_name(self):
        full_name = self.name
        size = self.size_from_name()
        if size:
            full_name = full_name.replace(size, '')
        if self.brand and not self.name.startswith(self.brand.name):
            full_name = self.brand.name + ' ' + full_name
        full_name = re.sub('\(.*\)', '' , full_name)
        return full_name

    def size_from_name(self):
        sizes = re.findall('[0-9,]+ *(?:g|ml|kg|gram|L|l|cl)', self.name)
        if sizes:
            return sizes[-1]
        return None

    def amount_from_name(self):
        size = self.size_from_name()
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
    user = models.ForeignKey(User)
    price_weight = models.IntegerField(default=0)
    environment_weight = models.IntegerField(default=0)
    social_weight = models.IntegerField(default=0)
    animals_weight = models.IntegerField(default=0)
    personal_health_weight = models.IntegerField(default=0)

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

class Ingredient(models.Model):
    quantity = models.IntegerField()
    unit = models.CharField(max_length=5, choices=ProductAmount.UNIT_CHOICES, default=ProductAmount.NO_UNIT)
    category = models.ForeignKey(Category)
    recipe = models.ForeignKey(Recipe)

    def __str__(self):
        return str(self.quantity) + ' ' + str(self.unit) + ' ' + str(self.category)

