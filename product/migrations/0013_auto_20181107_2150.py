# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-11-07 20:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0012_auto_20181107_2126'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='score_creator',
        ),
        migrations.AddField(
            model_name='food',
            name='score_creator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='product.ScoreCreator'),
        ),
        migrations.AddField(
            model_name='scorecreator',
            name='name',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
