# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-10-14 15:07
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_remove_food_mass_equivalent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipeitem',
            name='unit',
        ),
    ]
