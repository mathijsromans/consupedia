# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-10-23 21:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AHEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ah_id', models.CharField(max_length=64, unique=True)),
                ('size', models.CharField(max_length=64)),
                ('name', models.CharField(max_length=256)),
                ('price', models.IntegerField()),
                ('date', models.DateField()),
            ],
        ),
    ]