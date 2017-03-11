from django.db import models
from django.contrib.auth.models import User
from product.models import Rating


# models.Manager
class rating_manager():

    @staticmethod
    def get_avarage_rating(product):
        ratings = Rating.objects.filter(product=product)
        n_ratings = ratings.count()
        if n_ratings == 0:
            return None

        return justarandomreturn

    @staticmethod
    def get_userrating(user):
        return 1

    @staticmethod
    def set_userrating(user):
        return 1
