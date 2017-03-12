from django.db import models
from django.db.models import Avg
from product.models import Rating


# models.Manager
class rating_manager():
    ingredientenlijst = [
        [4, 'uien'],
        [500, 'g', 'preien'],
        [40, 'g', 'boter'],
        [2, 'el', 'olijfolie'],
        [1, 'el', 'gedroogde tijm'],
        [2, 'blaadjes', 'laurierblaadjes'],
        [198, 'g', 'corned beef'],
        [2, 'kg', 'gezeefde tomaten'],
        [1, 'kg', 'half-om-halfgehakt']]

ProductService().get_all_products(search_query)

    @staticmethod
    def create_recipe( name, ing)
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
