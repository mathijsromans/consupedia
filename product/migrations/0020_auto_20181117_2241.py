# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-11-17 21:41
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0019_auto_20181117_1838'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='author_if_user',
            new_name='user',
        ),
    ]