# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-11-07 17:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_questionmarkusage'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionmarkentry',
            name='usages',
            field=models.ManyToManyField(to='api.QuestionmarkUsage'),
        ),
    ]
