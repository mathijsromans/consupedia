# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-12-16 11:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0021_auto_20171216_0041'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Ingredient',
            new_name='RecipeItem',
        ),
    ]
