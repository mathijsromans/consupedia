# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-11-07 17:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20181107_1716'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionmarkUsage',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256)),
            ],
        ),
    ]
