# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-12-17 11:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0025_auto_20171216_1652'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='picture_url',
            field=models.CharField(default='', max_length=256),
            preserve_default=False,
        ),
    ]
