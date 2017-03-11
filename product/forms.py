from django import forms
from django.core.exceptions import ValidationError


def validate_price(value):
    if value < 0:
        raise ValidationError("Value cannot be below 0")


class ProductForm(forms.Form):
    name = forms.CharField(label='Name', max_length=100)
    price = forms.IntegerField(label='Price (cents)',validators=[validate_price])

class UserPreferenceForm(forms.Form):
    price_weight = forms.IntegerField(label='Value1')
    sustainability_weight = forms.IntegerField(label='Value2')
    quality_weight = forms.IntegerField(label='Value3')
