import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from product.models import ScoreCreator, FoodProperty, FoodPropertyType
from api import allerhande_scraper

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        land_use_property_type = FoodPropertyType.objects.get(name='landgebruik')
        animal_harm_type = FoodPropertyType.objects.get(name='dierenleed')
        if not land_use_property_type:
            print('land_use_property_type not found')
            return
        if not animal_harm_type:
            print('animal_harm_type not found')
            return
        for sc in ScoreCreator.objects.all():
            print('{}'.format(sc))
            for food in sc.food_set.all():
                print('  {}'.format(food))
                try:
                    FoodProperty.objects.get(type=land_use_property_type, food=food)
                    print('property found!')
                except FoodProperty.DoesNotExist:
                    fp = FoodProperty.objects.create(
                        type=land_use_property_type,
                        food=food,
                        value_float=sc.production_in_ton_per_ha,
                        source=sc.sources,
                        created_by=sc.user)
                    print('property {} created'.format(fp))
                try:
                    FoodProperty.objects.get(type=animal_harm_type, food=food)
                    print('property found!')
                except FoodProperty.DoesNotExist:
                    fp = FoodProperty.objects.create(
                        type=animal_harm_type,
                        food=food,
                        value_float=sc.killed_animal_iq_points,
                        source=sc.sources,
                        created_by=sc.user)
                    print('property {} created'.format(fp))

