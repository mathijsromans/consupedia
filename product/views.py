import json
import logging

from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from .models import Product, Food
from .management.commands.create_recipes import Command
from .models import Rating, Recipe, RecipeItem
from .models import UserPreferences
from .productservice import ProductService, RecipeService
from .forms import ProductForm, RecipeForm, RecipeURLForm, IngredientForm
from .forms import UserPreferenceForm
from .algorithms import set_score, recommended_products
from product.algorithms import ProductChooseAlgorithm

logger = logging.getLogger(__name__)


class ProductsView(TemplateView):
    template_name = 'product/products.html'

    def get_context_data(self, **kwargs):
        search_query = self.request.GET.get('search_box', None)
        if search_query:
            products_all = ProductService.search_products(search_query)
        else:
            products_all = ProductService.get_all_products()
        paginator = Paginator(products_all, 100)
        page = self.request.GET.get('page')
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
        context = super().get_context_data(**kwargs)
        context['products'] = products
        context['n_products_all'] = products_all.count()
        return context

class IngredientsView(TemplateView):
    template_name = 'ingredient/ingredients.html'

    def dispatch(self, request, *args, **kwargs):
        create_query = self.request.GET.get('create_box', None)
        if create_query:
            food, created = Food.objects.get_or_create(name=create_query)
            ProductService.update_products(food)
            return redirect(reverse('food-products-edit', args=(food.id,)))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ingredients'] = Food.objects.all().order_by('name')
        return context


class IngredientProductsEditView(TemplateView):
    template_name = 'ingredient/ingredient_products_edit.html'

    def get_context_data(self, ingredient_id, **kwargs):
        food = Food.objects.get(id=ingredient_id)
        context = super().get_context_data(**kwargs)
        context['anonymous_can_edit'] = True
        context['food'] = food
        return context


class RecipesView(TemplateView):
    template_name = 'recipe/recipe_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipes = Recipe.objects.all()
        context['recipes'] = recipes
        return context


def calculateTotalScores(recipe, up):
    print('SCORING')
    for recipe_item in recipe.recipeitem_set.all():
        product = recipe_item.recommended_product(up)
        if product:
            scores = ProductChooseAlgorithm.calculate_product_score(product, up)
            print(scores)
    total_price_weight = recipe.calculateTotalPriceWeight(up) * up.price_weight
    total_environment_weight = -recipe.calculateTotalEnvironmentWeight(up) * up.environment_weight
    total_social_weight = -recipe.calculateTotalSocialWeight(up) * up.social_weight
    total_animals_weight = -recipe.calculateTotalAnimalsWeight(up) * up.animals_weight
    total_personal_health_weight = -recipe.calculateTotalPersonalHealthWeight(up) * up.personal_health_weight
    return {'total_price_weight': total_price_weight,
            'total_environment_weight':total_environment_weight,
            'total_social_weight': total_social_weight,
            'total_animals_weight': total_animals_weight,
            'total_personal_health_weight': total_personal_health_weight}


def calculateTotalScore(recipe, up):
    scores = calculateTotalScores(recipe, up)
    return scores['total_price_weight'] + \
        scores['total_environment_weight'] + \
        scores['total_social_weight'] + \
        scores['total_animals_weight'] + \
        scores['total_personal_health_weight']


class RecipeDetailView(TemplateView):
    template_name = 'recipe/recipe_show.html'

    def get_context_data(self, recipe_id, **kwargs):
        context = super().get_context_data(**kwargs)
        recipe = Recipe.objects.get(id=recipe_id)
        up, created = UserPreferences.objects.get_or_create( user = self.request.user )
        ingredient_and_price_list = [(recipe_item, recipe_item.price_str(up)) for recipe_item in recipe.recipeitem_set.all() ]
        context['recipe'] = recipe
        context['ingredient_and_price_list'] = ingredient_and_price_list
        totalScores = calculateTotalScores(recipe, up)
        score_text = "Prijs: " + format(totalScores['total_price_weight'], '.2f') + ", "
        score_text += "Mileu: " + format(totalScores['total_environment_weight'], '.2f') + ", "
        score_text += "Sociaal: " + format(totalScores['total_social_weight'], '.2f') + ", "
        score_text += "Dierenwelzijn: " + format(totalScores['total_animals_weight'], '.2f') + ", "
        score_text += "Gezondheid: " + format(totalScores['total_personal_health_weight'], '.2f')
        context['recipe_score_text'] = score_text
        context['recipe_total_score_text'] = format(calculateTotalScore(recipe, up), '.2f')
        return context


class RecipeAddView(FormView):
    template_name = 'recipe/recipe_add.html'
    form_class = RecipeURLForm
    success_url = '/recipes/'

    def get_initial(self, **kwargs):
        return {'url': 'R-R399568',
                'quantity': 1}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
#        context['url'] = 'R-R399568'
        return context

    @transaction.atomic
    def form_valid(self, form):
        recipe, ingredients_created = RecipeService.create_recipe_from_ah_id(
            form.cleaned_data['url'],
            form.cleaned_data['provides'],
            form.cleaned_data['quantity'])
        logger.info('CREATED RECIPE ' + str(recipe))
        ingredients_created = list(recipe.recipeitem_set.values_list('ingredient_id', flat=True))
        recipe_id = recipe.id if recipe else 0
        if not ingredients_created:
            return redirect('recipe_detail', args=[recipe_id])
        return redirect(reverse('recipe-edit-new', args=[recipe_id, json.dumps(ingredients_created)]))


class RecipeEditNewView(TemplateView):
    template_name = 'recipe/recipe_edit_new.html'

    def get_context_data(self, recipe_id, ingredients_created, **kwargs):
        ingredients_created = json.loads(ingredients_created)
        context = super().get_context_data()
        context['recipe'] = Recipe.objects.get(id=recipe_id)
        context['ingredients_created'] = Food.objects.filter(id__in=ingredients_created) if ingredients_created is not None else None
        return context


class RecipeEditView(FormView):
    template_name = 'recipe/recipe_edit.html'
    form_class = RecipeForm
    success_url = '/recipes/'
    recipe = None
    
    def get_initial(self, **kwargs):
        if 'recipe_id' in self.kwargs:
            recipe_id = self.kwargs['recipe_id']
            self.recipe = Recipe.objects.get(id=recipe_id )
            return {'name': self.recipe.name}
        return None       

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'recipe_id' in self.kwargs:
            recipe_id = self.kwargs['recipe_id']
            self.recipe = Recipe.objects.get(id=recipe_id )
            context['recipe'] = self.recipe
        return context

    @transaction.atomic
    def form_valid(self, form):
        Recipe.objects.create(name=form.cleaned_data['name'])
        return super().form_valid(form)


class ProductView(TemplateView):
    template_name = 'product/product_page.html'

    def get_context_data(self, product_id, **kwargs):
        context = super().get_context_data(**kwargs)
        product = Product.objects.get(id=product_id)
        up, created = UserPreferences.objects.get_or_create( user = self.request.user )
        set_score(product, up)
        context['product'] = product
        return context


class IngredientView(TemplateView):
    template_name = 'ingredient/ingredient.html'

    def get_context_data(self, ingredient_id, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            food = Food.objects.get(id=ingredient_id)
            context['food'] = food
            if self.request.user.is_authenticated():
                up, created = UserPreferences.objects.get_or_create(user=self.request.user)
                product_list = recommended_products(food, up)
                context['product_list'] = product_list
                context['product'] = product_list[0] if product_list else None
        except ObjectDoesNotExist:
            pass
        return context


def remove_ingredient_product(request):
    Product.objects.get(id=int(request.POST['product_id'])).delete()
    response = json.dumps({'status': 'success'})
    return HttpResponse(response, content_type='application/json')


class ProductCreateView(FormView):
    template_name = 'product/product_add.html'
    form_class = ProductForm
    success_url = '/products/'

    @transaction.atomic
    def form_valid(self, form):
        Product.objects.create(name=form.cleaned_data['name'], price=form.cleaned_data['price'])
        return super().form_valid(form)


class ProductEditView(FormView):
    template_name = 'product/product_edit.html'
    form_class = ProductForm
    success_url = '/'

    @property
    def product(self):
        return Product.objects.get(id=self.kwargs['product_id'])

    def get_initial(self):
        return {'name': self.product.name, 'price': self.product.price}

    @transaction.atomic
    def form_valid(self, form):
        product = self.product
        product.name = form.cleaned_data['name']
        product.price = form.cleaned_data['price']
        product.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        return context

class IngredientEditView(FormView):
    template_name = 'ingredient/ingredient_edit.html'
    form_class = IngredientForm

    @property
    def success_url(self):
        return '/recipe/' + str(self.recipe_item.recipe.id)

    @property
    def recipe_item(self):
        return RecipeItem.objects.get(id=self.kwargs['ingredient_id'])

    def get_initial(self):
        return {'quantity': self.recipe_item.quantity,
                'unit': self.recipe_item.unit,
                'food': self.recipe_item.food}

    @transaction.atomic
    def form_valid(self, form):
        recipe_item = self.recipe_item
        recipe_item.quantity = form.cleaned_data['quantity']
        recipe_item.unit = form.cleaned_data['unit']
        recipe_item.food = form.cleaned_data['food']
        recipe_item.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recipe_item'] = self.recipe_item
        return context

class UserPreferenceEditView(FormView):
    template_name = 'user/user_preference_edit.html'
    form_class = UserPreferenceForm
    success_url = '/'

    def get_my_preference(self):
        return UserPreferenceEditView.get_my_preference_by_request(self.request)

    @staticmethod
    def get_my_preference_by_request(request):
        up, created = UserPreferences.objects.get_or_create( user = request.user )
        return up

    def get_initial(self):
        return {'price_weight': self.get_my_preference().price_weight,
                'environment_weight': self.get_my_preference().environment_weight,
                'social_weight': self.get_my_preference().social_weight,
                'animals_weight': self.get_my_preference().animals_weight,
                'personal_health_weight': self.get_my_preference().personal_health_weight}

    @transaction.atomic
    def form_valid(self, form):
        userPreference = self.get_my_preference()
        userPreference.price_weight = form.cleaned_data['price_weight']
        userPreference.environment_weight = form.cleaned_data['environment_weight']
        userPreference.social_weight = form.cleaned_data['social_weight']
        userPreference.animals_weight = form.cleaned_data['animals_weight']
        userPreference.personal_health_weight = form.cleaned_data['personal_health_weight']
        userPreference.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['userPreference'] = self.get_my_preference()
        return context
        

class WhatToEatView(TemplateView):
    template_name = 'product/what_to_eat.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Food.objects.all().order_by('name')
        return context


@login_required
def set_product_rating(request):
    product = Product.objects.get(id=request.POST['product_id'])
    product.set_rating(request.user, int(request.POST['rating']))
    ratings = product.get_rating(request.user)
    user_rating = None
    if ratings.exists():
        user_rating = ratings[0].rating

    average_rating = product.get_average_rating()
    response = json.dumps({'status': 'success', 'user_rating': str(user_rating), 'average_rating': str(average_rating)})
    return HttpResponse(response, content_type='application/json')
    
def get_what_to_eat_result(request):
    food = Food.objects.get(id=request.POST['ingredient_id'])
    up = UserPreferences()
    #todo get user preferences from post request.
    up.price_weight = 5
    up.environment_weight = 5
    up.social_weight = 5
    up.animals_weight = 5
    up.personal_health_weight = 5
    result = ProductChooseAlgorithm.maximize_product_scores(up, food)
    scores = result.scores
  
    data = serializers.serialize('json', [result, scores, ])
    return HttpResponse(data, content_type='application/json')

@login_required
def set_user_preference_data(request):
    up = UserPreferenceEditView.get_my_preference_by_request(request)

    pref_to_change = request.POST['user_preference']
    new_weight = int(request.POST['weight'])

    if pref_to_change == 'price':
        up.price_weight = new_weight
    elif pref_to_change == 'environment':
        up.environment_weight = new_weight
    elif pref_to_change == 'social':
        up.social_weight = new_weight
    elif pref_to_change == 'animals':
        up.animals_weight = new_weight
    elif pref_to_change == 'personal_health':
        up.personal_health_weight = new_weight
    up.save()
    return get_user_preference_data(up)

@login_required
def get_user_preference_data(up):
    rel = up.get_rel_weights()
    response = json.dumps({'status': 'success',
                           'user_preferences': [
                               { "preference": "price",
                                 "weight": up.price_weight,
                                 "rel_weight": rel[0] },
                               { "preference": "environment",
                                 "weight": up.environment_weight,
                                 "rel_weight": rel[1] },
                               { "preference": "social",
                                 "weight": up.social_weight,
                                 "rel_weight": rel[2] },
                               { "preference": "animals",
                                 "weight": up.animals_weight,
                                 "rel_weight": rel[3] },
                               { "preference": "personal_health",
                                 "weight": up.personal_health_weight,
                                 "rel_weight": rel[4] } ] })
    return HttpResponse(response, content_type='application/json')

@login_required
def get_recipes_for_user(request):

    up = UserPreferenceEditView.get_my_preference_by_request(request)
    #Find all recipes
    recipes = Recipe.objects.all()
    #Order recipes based on userpreference    
    tupelDictionary = [(calculateTotalScore(entry, up), entry) for entry in recipes]
    tupelDictionary.sort(key=lambda tup: tup[0])
    sortedList = [entry for sortKey, entry in tupelDictionary]

    #Return first 6 results.
    list_result = [{'name': entry.name, 
                    'number_persons': entry.number_persons,
                    'preparation_time_in_min': entry.preparation_time_in_min,
                    'content': entry.number_persons,
                    'id': entry.id,
                    'picture_url': entry.picture_url} for entry in sortedList]
    
    response = json.dumps({'status': 'success',
                           'recipes': list_result })                                      
    return HttpResponse(response, content_type='application/json')