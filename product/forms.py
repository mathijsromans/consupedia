from django import forms
from django.core.exceptions import ValidationError
from product.models import Ingredient

def validate_price(value):
    if value < 0:
        raise ValidationError("Value cannot be below 0")


class ProductForm(forms.Form):
    name = forms.CharField(label='Name', max_length=100)
    price = forms.IntegerField(label='Price (cents)',validators=[validate_price])


class IngredientForm(forms.Form):
    quantity = forms.IntegerField(label='quantity')
    unit = forms.CharField(label='unit', max_length=5)
    ingredient = forms.ModelChoiceField(label='ingredient', queryset=Ingredient.objects.all().order_by('name'))
    # category = forms.ModelChoiceField(label='category', queryset=Category.objects.all().sort(key=lambda c: c.name))


class UserPreferenceForm(forms.Form):
    price_weight = forms.IntegerField(label='Prijs')
    environment_weight = forms.IntegerField(label='Milieu')
    social_weight = forms.IntegerField(label='Mensenrechten')
    animals_weight = forms.IntegerField(label='Dieren')
    personal_health_weight = forms.IntegerField(label='Gezond')


class RecipeURLForm(forms.Form):
    url = forms.CharField(label='url', max_length=256)


class RecipeForm(forms.Form):
    name = forms.CharField(label='Name', max_length=256)
 