# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-26 14:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0019_auto_20170325_1623'),
    ]

    operations = [
        migrations.AddField(
            model_name='productprice',
            name='product_name',
            field=models.CharField(default='', max_length=256),
            preserve_default=False,
        ),
    ]