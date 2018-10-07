from django import forms
from django.core.exceptions import ValidationError
from product.models import Food
from product.amount import ProductAmount


def validate_price(value):
    if value < 0:
        raise ValidationError("Value cannot be below 0")


class ProductForm(forms.Form):
    name = forms.CharField(label='Name', max_length=100)
    price = forms.IntegerField(label='Price (cents)',validators=[validate_price])


class RecipeItemForm(forms.Form):
    quantity = forms.IntegerField(label='Quantity')
    unit = forms.CharField(label='Unit', max_length=5)
    food = forms.ModelChoiceField(label='Food', queryset=Food.objects.all().order_by('name'))


class FoodForm(forms.Form):
    name = forms.CharField(label='Naam', max_length=256)
    unit = forms.ChoiceField(label='Eenheid', choices=ProductAmount.UNIT_CHOICES)
    mass_equivalent = forms.IntegerField(label='Equivalent gewicht (g)')


class UserPreferenceForm(forms.Form):
    price_weight = forms.IntegerField(label='Prijs')
    environment_weight = forms.IntegerField(label='Milieu')
    social_weight = forms.IntegerField(label='Mensenrechten')
    animals_weight = forms.IntegerField(label='Dieren')
    personal_health_weight = forms.IntegerField(label='Gezond')


class RecipeURLForm(forms.Form):
    url = forms.CharField(label='url', max_length=256)
    provides = forms.ModelChoiceField(label='resultaat', empty_label=None, queryset=Food.objects.all().order_by('name'))
    quantity = forms.IntegerField(label='hoeveelheid', min_value=1)


class RecipeForm(forms.Form):
    name = forms.CharField(label='Name', max_length=256)
#    provides = forms.ModelChoiceField(label='resultaat', empty_label=None, queryset=Food.objects.all().order_by('name'))
    quantity = forms.IntegerField(label='hoeveelheid', min_value=1)
