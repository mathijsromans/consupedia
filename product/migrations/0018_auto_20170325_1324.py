# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-25 12:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0017_auto_20170320_2323'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductAtShop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime_created', models.DateTimeField(auto_now_add=True)),
                ('price', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80)),
            ],
        ),
        migrations.RemoveField(
            model_name='product',
            name='price',
        ),
        migrations.AddField(
            model_name='productatshop',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.Product'),
        ),
        migrations.AddField(
            model_name='productatshop',
            name='shop',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.Shop'),
        ),
        migrations.AddField(
            model_name='product',
            name='available',
            field=models.ManyToManyField(through='product.ProductAtShop', to='product.Shop'),
        ),
    ]