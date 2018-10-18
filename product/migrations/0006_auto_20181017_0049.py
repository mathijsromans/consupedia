# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-10-16 22:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0005_auto_20181017_0046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='brand',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='product.Brand'),
        ),
        migrations.AlterField(
            model_name='product',
            name='ean_code',
            field=models.CharField(blank=True, max_length=25, null=True),
        ),
    ]
