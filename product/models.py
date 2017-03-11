from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=256, null=True)
    ean_code = models.CharField(max_length=25, null=True)
    price = models.IntegerField(null=True)


class UserPreferences(models.Model):
    user = models.ForeignKey(User)

    def __str__(self):
        return 'Preferences of ' + self.user.username
