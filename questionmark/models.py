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
