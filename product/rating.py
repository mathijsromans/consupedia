from django.db import models
from django.db.models import Avg
from product.models import Rating


# models.Manager
class rating_manager():

    @staticmethod
    def get_avarage_rating(product):
        ratings = Rating.objects.filter(product=product).aggregate(Avg('rating'))
        return ratings['rating__avg']

    @staticmethod
    def get_userrating(user, product):
        rating = Rating.objects.filter(user=user, product=product)
        return rating

    @staticmethod
    def set_rating(user, product, rating):
        ratings = Rating.objects.filter(product=product, user=user)
        if ratings:
            rating_obj = ratings[0]
        else:
            rating_obj = Rating(product=product, user=user)
        rating_obj.rating = rating
        rating_obj.save()
