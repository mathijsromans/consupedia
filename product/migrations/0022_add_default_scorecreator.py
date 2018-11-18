import uuid

from django.db import migrations
from django.contrib.auth.hashers import make_password


def create_admin_user(apps, schema_editor):
    User = apps.get_registered_model('auth', 'User')
    user_default = User(
        username='default',
        email='default@default.com',
        password=make_password(uuid.uuid4().hex),
        is_superuser=False,
        is_staff=False
    )
    user_default.save()


def create_types(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Type = apps.get_model("product", "ScoreCreator")
    User = apps.get_registered_model('auth', 'User')
    user_default = User.objects.get(email='default@default.com')
    score_creators = Type.objects.using(db_alias).filter(name="default")
    if not score_creators.exists():
        Type.objects.using(db_alias).create(name="default", user=user_default)


class Migration(migrations.Migration):

    dependencies = [
         ('product', '0021_auto_20181117_2332'),
    ]

    operations = [
        migrations.RunPython(create_admin_user),
        migrations.RunPython(create_types),
    ]
