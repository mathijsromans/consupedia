# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2019-01-21 23:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0030_auto_20190121_2239'),
    ]

    operations = [
        migrations.AlterField(
            model_name='foodpropertytype',
            name='combine_strategy',
            field=models.CharField(choices=[('OR', 'Logische of'), ('AND', 'Logische en'), ('PLUS', 'Optellen')], max_length=5),
        ),
    ]
