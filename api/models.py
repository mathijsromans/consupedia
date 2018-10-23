from django.db import models


class QuestionMarkQuery(models.Model):
    params_as_string = models.CharField(max_length=256)
    json = models.TextField()

    def __str__(self):
        return 'QuestionMark query: ' + self.params_as_string


class JumboQuery(models.Model):
    q_product_name = models.CharField(max_length=256)
    html = models.TextField()
    

class AHQuery(models.Model):
    q_product_name = models.CharField(max_length=256)
    json = models.TextField()


class AHEntry(models.Model):
    ah_id = models.CharField(max_length=64, unique=True)
    size = models.CharField(max_length=64)
    name = models.CharField(max_length=256)
    price = models.IntegerField()
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'AH Entry {}~{}~{}'.format(self.name, self.size, self.price)


class JumboEntry(models.Model):
    size = models.CharField(max_length=64)
    name = models.CharField(max_length=256)
    price = models.IntegerField()
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Jumbo Entry {}~{}~{}'.format(self.name, self.size, self.price)

