from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):

    @property
    def name(self):
        names = ProductName.objects.filter(product=self).order_by('-datetime_created')
        if names:
            return names[0]
        return None

    @property
    def price(self):
        prices = Price.objects.filter(product=self).order_by('-datetime_created')
        if prices:
            return prices[0]
        return None


class Revision(models.Model):
    user = models.ForeignKey(User)
    datetime_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-datetime_created']

    def __str__(self):
        return self.user.username + ' ' + str(self.datetime_created)


class ProductName(Revision):
    name = models.CharField(max_length=300)
    product = models.ForeignKey(Product)

    def __str__(self):
        return self.name


class Price(Revision):
    cent = models.IntegerField(default=0)
    product = models.ForeignKey(Product)

    def __str__(self):
        return str(self.cent)
