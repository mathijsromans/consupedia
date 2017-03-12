from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg

class Category(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Score(models.Model):
    environment = models.IntegerField(null=True)
    social = models.IntegerField(null=True)
    animals = models.IntegerField(null=True)
    personal_health = models.IntegerField(null=True)


class Product(models.Model):
    name = models.CharField(max_length=256, null=True)
    ean_code = models.CharField(max_length=25, null=True)
    price = models.IntegerField(null=True)
    size = models.CharField(max_length=256, null=True)
    amount_in_gram = models.IntegerField(null=True)
    category = models.ForeignKey(Category, null=True)
    scores = models.OneToOneField(Score, null=True)
    thumb_url = models.CharField(max_length=256, null=True)
    product_score = 0
    product_score_details = ''

    def set_rating(self, user, rating_value):
        ratings = Rating.objects.filter(product=self, user=user)
        if ratings.exists():
            rating = ratings[0]
            rating.rating = rating_value
            rating.save()
        else:
            rating = Rating.objects.create(product=self, user=user, rating=rating_value)

    def get_rating(self, user):
        rating = Rating.objects.filter(product=self, user=user)
        return rating

    def get_average_rating(self):
        ratings = Rating.objects.filter(product=self).aggregate(Avg('rating'))
        return ratings['rating__avg']



class UserPreferences(models.Model):
    user = models.ForeignKey(User)
    price_weight = models.IntegerField(default=0)
    environment_weight = models.IntegerField(default=0)
    social_weight = models.IntegerField(default=0)
    animals_weight = models.IntegerField(default=0)
    personal_health_weight = models.IntegerField(default=0)

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
    NO_UNIT = '-'
    GRAM = 'g'
    ML = 'ml'
    UNIT_CHOICES = (
        (NO_UNIT, '-'),
        (GRAM, 'g'),
        (ML, 'ml')
    )
    quantity = models.IntegerField()
    unit = models.CharField(max_length=5, choices=UNIT_CHOICES, default=NO_UNIT)
    category = models.ForeignKey(Category)
    recipe = models.ForeignKey(Recipe)

    def __str__(self):
        return str(self.quantity) + ' ' + str(self.unit) + ' ' + str(self.category)

