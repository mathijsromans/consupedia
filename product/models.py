from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=256)

class Score(models.Model):
    environment = models.IntegerField(null=True)
    social = models.IntegerField(null=True)
    animals = models.IntegerField(null=True)
    personal_health = models.IntegerField(null=True)


class Product(models.Model):
    name = models.CharField(max_length=256, null=True)
    ean_code = models.CharField(max_length=25, null=True)
    price = models.IntegerField(null=True)
    category = models.ForeignKey(Category, null=True)
    scores = models.OneToOneField(Score, null=True)


class UserPreferences(models.Model):
    user = models.ForeignKey(User)
    price_weight = models.IntegerField(default=0)
    environment_weight = models.IntegerField(default=0)
    social_weight = models.IntegerField(default=0)
    animals_weight = models.IntegerField(default=0)
    personal_health_weight = models.IntegerField(default=0)

    def __str__(self):
        return 'Preferences of ' + self.user.username
