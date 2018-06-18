# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-06-14 20:44
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='Food',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('unit', models.CharField(choices=[('-', 'st.'), ('g', 'g'), ('ml', 'ml'), ('el', 'el'), ('tl', 'tl')], default='-', max_length=5)),
                ('provides', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='product.Food')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, null=True)),
                ('questionmark_id', models.IntegerField(default=0)),
                ('ean_code', models.CharField(max_length=25, null=True)),
                ('quantity', models.IntegerField(default=0)),
                ('unit', models.CharField(choices=[('-', 'st.'), ('g', 'g'), ('ml', 'ml'), ('el', 'el'), ('tl', 'tl')], default='-', max_length=5)),
                ('thumb_url', models.CharField(max_length=256, null=True)),
                ('version', models.IntegerField(default=1)),
                ('brand', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='product.Brand')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.Food')),
            ],
        ),
        migrations.CreateModel(
            name='ProductPrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=256)),
                ('price', models.IntegerField()),
                ('datetime_created', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.Product')),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.Product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('quantity', models.IntegerField()),
                ('source_if_not_user', models.CharField(max_length=256)),
                ('number_persons', models.IntegerField(default=0)),
                ('preparation_time_in_min', models.IntegerField(default=0)),
                ('picture_url', models.CharField(max_length=256)),
                ('preparation', models.TextField()),
                ('author_if_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('provides', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.Food')),
            ],
        ),
        migrations.CreateModel(
            name='RecipeItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('unit', models.CharField(choices=[('-', 'st.'), ('g', 'g'), ('ml', 'ml'), ('el', 'el'), ('tl', 'tl')], default='-', max_length=5)),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.Food')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.Recipe')),
            ],
        ),
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('environment', models.IntegerField(null=True)),
                ('social', models.IntegerField(null=True)),
                ('animals', models.IntegerField(null=True)),
                ('personal_health', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80)),
            ],
        ),
        migrations.CreateModel(
            name='UserPreferences',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price_weight', models.IntegerField(default=50)),
                ('environment_weight', models.IntegerField(default=50)),
                ('social_weight', models.IntegerField(default=50)),
                ('animals_weight', models.IntegerField(default=50)),
                ('personal_health_weight', models.IntegerField(default=50)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='productprice',
            name='shop',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.Shop'),
        ),
        migrations.AddField(
            model_name='product',
            name='prices',
            field=models.ManyToManyField(through='product.ProductPrice', to='product.Shop'),
        ),
        migrations.AddField(
            model_name='product',
            name='scores',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='product.Score'),
        ),
        migrations.AlterUniqueTogether(
            name='rating',
            unique_together=set([('user', 'product')]),
        ),
    ]
