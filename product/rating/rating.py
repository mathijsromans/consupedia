from django.db import models
from django.contrib.auth.models import User
from product.models import Product


class Rating(models.Model):
    user = models.ForeignKey(User)
    product = models.ForeignKey(Product)
    rating = models.IntegerField(null=False)

    class Meta:
        unique_together = ('user', 'product')

# getters and setters for ratings


class ratingManager(models.Manager):

    def __init__(self, product):
        self.product = product

    def get_avarage_rating(self):
        return 0

    def get_userrating(self, user):
        return 1

    def set_userrating(self, user):
        return 1
