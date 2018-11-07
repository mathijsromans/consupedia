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


class QuestionmarkTheme(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class QuestionmarkCertificate(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=256)
    image_url = models.CharField(max_length=256)
    themes = models.ManyToManyField(QuestionmarkTheme)

    def __str__(self):
        return 'Certificate {}'.format(self.name)


class QuestionmarkEntry(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=256)
    brand = models.CharField(max_length=256)
    thumb_url = models.CharField(max_length=256)
    date = models.DateTimeField(auto_now=True)
    score_environment = models.IntegerField(blank=True, null=True, default=None)
    score_social = models.IntegerField(blank=True, null=True, default=None)
    score_animals = models.IntegerField(blank=True, null=True, default=None)
    score_personal_health = models.CharField(max_length=20, blank=True, null=True, default=None)
    certificates = models.ManyToManyField(QuestionmarkCertificate)

    def __str__(self):
        return 'Questionmark Entry {}'.format(self.name)

