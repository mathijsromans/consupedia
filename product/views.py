import json

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

from .models import Product, Category
from .management.commands.create_recipes import Command
from .models import Rating, Recipe, Ingredient
from .models import UserPreferences
from .productservice import ProductService, RecipeService
from .forms import ProductForm, RecipeForm, RecipeURLForm, IngredientForm
from .forms import UserPreferenceForm
from .algorithms import set_score, recommended_products
from product.algorithms import ProductChooseAlgorithm


class ProductsView(TemplateView):
    template_name = 'product/products.html'

    def get_context_data(self, **kwargs):
        if self.request.method == 'GET': # If the form is submitted
            search_query = self.request.GET.get('search_box', None)
        context = super().get_context_data(**kwargs)
        products_all = ProductService().get_all_products(search_query)
        paginator = Paginator(products_all, 100)
        page = self.request.GET.get('page')
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
        context['products'] = products
        context['n_products_all'] = products_all.count()
        return context

class CategoriesView(TemplateView):
    template_name = 'category/categories.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class RecipesView(TemplateView):
    template_name = 'recipe/recipe_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipes = Recipe.objects.all()
        if not recipes:
            Command.create_recipe('R-R399568')   # create a default recipe so there is something to show
            recipes = Recipe.objects.all()
        context['recipes'] = recipes
        return context


class RecipeDetailView(TemplateView):
    template_name = 'recipe/recipe_show.html'

    def get_context_data(self, recipe_id, **kwargs):
        context = super().get_context_data(**kwargs)
        recipe = Recipe.objects.get(id=recipe_id)
        up, created = UserPreferences.objects.get_or_create( user = self.request.user )
        ingredient_and_price_list = [(ingredient, ingredient.price_str(up)) for ingredient in recipe.ingredient_set.all() ]
        context['recipe'] = recipe
        context['ingredient_and_price_list'] = ingredient_and_price_list
        return context


class RecipeAddView(FormView):
    template_name = 'recipe/recipe_add.html'
    form_class = RecipeURLForm
    success_url = '/recipes/'

    def get_initial(self, **kwargs):
        return {'url': 'R-R399568'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url'] = 'R-R399568'
        return context

    @transaction.atomic
    def form_valid(self, form):
        recipe = Command.create_recipe(form.cleaned_data['url'])
        print('CREATED RECIPE ' + str(recipe))
        recipe_id = recipe.id if recipe else 0
        return redirect(reverse('recipe_detail', args=[recipe_id]))


class RecipeEditView(FormView):
    template_name = 'recipe/recipe_edit.html'
    form_class = RecipeForm
    success_url = '/recipes/'
    recipe = None;
    
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


class CategoryView(TemplateView):
    template_name = 'category/category.html'

    def get_context_data(self, category_id, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            category = Category.objects.get(id=category_id)
            context['category'] = category
            if self.request and self.request.user and self.request.user.is_authenticated():
                up, created = UserPreferences.objects.get_or_create(user=self.request.user)
                product_list = recommended_products(category, up)
                context['product'] = product_list[0] if product_list else None
                context['all_products'] = product_list
        except ObjectDoesNotExist:
            pass
        return context


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
        return '/recipe/' + str(self.ingredient.recipe.id)

    @property
    def ingredient(self):
        return Ingredient.objects.get(id=self.kwargs['ingredient_id'])

    def get_initial(self):
        return {'quantity': self.ingredient.quantity,
                'unit': self.ingredient.unit,
                'category': self.ingredient.category}

    @transaction.atomic
    def form_valid(self, form):
        ingredient = self.ingredient
        ingredient.quantity = form.cleaned_data['quantity']
        ingredient.unit = form.cleaned_data['unit']
        ingredient.category = form.cleaned_data['category']
        ingredient.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ingredient'] = self.ingredient
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
        context['categories'] = Category.objects.all().order_by('name')
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
    category = Category.objects.get(id=request.POST['category_id'])   
    up = UserPreferences()
    #todo get user preferences from post request.
    up.price_weight = 5
    up.environment_weight = 5
    up.social_weight = 5
    up.animals_weight = 5
    up.personal_health_weight = 5
    result = ProductChooseAlgorithm.maximize_product_scores(up, category)
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
                                 "weight:": up.price_weight,
                                 "rel_weight": rel[0] },
                               { "preference": "environment",
                                 "weight:": up.environment_weight,
                                 "rel_weight": rel[1] },
                               { "preference": "social",
                                 "weight:": up.social_weight,
                                 "rel_weight": rel[2] },
                               { "preference": "animals",
                                 "weight:": up.animals_weight,
                                 "rel_weight": rel[3] },
                               { "preference": "personal_health",
                                 "weight:": up.personal_health_weight,
                                 "rel_weight": rel[4] } ] })
    return HttpResponse(response, content_type='application/json')
