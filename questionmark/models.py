from django.db import models

class QuestionMarkQuery(models.Model):
    q_product_name = models.CharField(max_length=256)
    json = models.TextField()


class JumboQuery(models.Model):
    q_product_name = models.CharField(max_length=256)
    html = models.TextField()