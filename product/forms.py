from django import forms


class ProductForm(forms.Form):
    name = forms.CharField(label='Name', max_length=100)
    price = forms.IntegerField(label='Price (cents)')
