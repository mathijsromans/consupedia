from django.db import migrations


def rename_food_names(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Food = apps.get_model("product", "Food")
    foods = Food.objects.using(db_alias).all()
    for food in foods:
        food.name = food.name.lower()
        food.save()


class Migration(migrations.Migration):

    dependencies = [
         ('product', '0022_add_default_scorecreator'),
    ]

    operations = [
        migrations.RunPython(rename_food_names),
    ]
