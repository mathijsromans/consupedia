# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-10-23 22:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_ahentry'),
    ]

    operations = [
        migrations.CreateModel(
            name='JumboEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.CharField(max_length=64)),
                ('name', models.CharField(max_length=256)),
                ('price', models.IntegerField()),
                ('date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AlterField(
            model_name='ahentry',
            name='date',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
