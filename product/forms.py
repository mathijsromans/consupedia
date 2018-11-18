from django import forms
from django.forms import formset_factory
from django.core.exceptions import ValidationError
from product.models import Food, ScoreCreator
from product.amount import ProductAmount


def validate_price(value):
    if value < 0:
        raise ValidationError("Value cannot be below 0")


class FoodWithUnitChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, food):
        return '(' + food.unit + ') ' + food.name


class ProductForm(forms.Form):
    food = FoodWithUnitChoiceField(label='', queryset=Food.objects.all().order_by('name'))


class RecipeItemForm(forms.Form):
    quantity = forms.IntegerField(label='')
    food = FoodWithUnitChoiceField(label='', queryset=Food.objects.all().order_by('name'))


class TestForm(forms.Form):
    quantity = forms.CharField(
        label='quantity',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Book Name here'
        })
    )

RecipeItemFormset = formset_factory(RecipeItemForm, extra=1)


class FoodForm(forms.Form):
    name = forms.CharField(label='Naam', max_length=256)
    unit = forms.ChoiceField(label='Eenheid', choices=ProductAmount.UNIT_CHOICES)
    equiv_weight = forms.FloatField(label='Equivalent gewicht in gram', required=False)
    score_creator = forms.ModelChoiceField(label='Cijfers', queryset=ScoreCreator.objects.all().order_by('name'), required=False)


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
    name = forms.CharField(label='Naam', max_length=256,
                           widget=forms.TextInput(attrs={'placeholder': 'Naam van recept...'}))
    provides = FoodWithUnitChoiceField(label='Resultaat', empty_label=None, queryset=Food.objects.all().order_by('name'))
    quantity = forms.IntegerField(label='Aantal', widget=forms.NumberInput(attrs={'placeholder': 'Hoeveelheid...'}))
    source_if_not_user = forms.CharField(label='Bron', initial='-', max_length=256, required=False,
                           widget=forms.TextInput())
    preparation_time_in_min = forms.IntegerField(label='Bereidingstijd in minuten', widget=forms.NumberInput(attrs={'placeholder': 'Bereidingstijd...'}))
    preparation = forms.CharField(label='Bereidingswijze', required=False,
                           widget=forms.Textarea(attrs={'placeholder': 'Bereidingswijze...'}))


class ScoreCreatorForm(forms.Form):

    name = forms.CharField(label='Naam', max_length=256,
                           widget=forms.TextInput(attrs={'placeholder': 'Naam van dit type eten...'}))
    production_in_ton_per_ha = forms.FloatField(label='Productie in ton per hectare', required=False)
    killed_animal_iq_points = forms.FloatField(label='Aantal hercencellen per kg', required=False)
    sources = forms.CharField(label='Bron', max_length=256, widget=forms.TextInput(attrs={'placeholder': 'Bron...'}))
