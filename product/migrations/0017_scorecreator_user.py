# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-11-17 17:33
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('product', '0016_auto_20181107_2310'),
    ]

    operations = [
        migrations.AddField(
            model_name='scorecreator',
            name='user',
            field=models.ForeignKey(default=4, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
