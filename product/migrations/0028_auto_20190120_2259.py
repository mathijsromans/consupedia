# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2019-01-20 21:59
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('product', '0027_userpreferences_prep_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='FoodProperty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value_bool', models.NullBooleanField(default=None)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('food', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.Food')),
            ],
        ),
        migrations.CreateModel(
            name='FoodPropertyType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('combine_strategy', models.CharField(choices=[('OR', 'Overerving - logische of')], max_length=5)),
            ],
        ),
        migrations.AddField(
            model_name='foodproperty',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.FoodPropertyType'),
        ),
        migrations.AddField(
            model_name='food',
            name='property_types',
            field=models.ManyToManyField(through='product.FoodProperty', to='product.FoodPropertyType'),
        ),
    ]