import json

from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Product, Category
from .management.commands.create_recipes import Command
from .models import Rating, Recipe
from .models import UserPreferences
from .productservice import ProductService, RecipeService
from .forms import ProductForm, RecipeForm
from .forms import UserPreferenceForm
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
        context['recipe'] = Recipe.objects.get(id=recipe_id)
        return context


class RecipeAddView(FormView):
    template_name = 'recipe/recipe_edit.html'
    form_class = RecipeForm
    success_url = '/recipes/'
    recipe = None;
    
    def get_initial(self, **kwargs):
        if ('recipe_id' in self.kwargs):
            recipe_id = self.kwargs['recipe_id']
            self.recipe = Recipe.objects.get(id=recipe_id )
            return {'name': self.recipe.name}
        return None       

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if ('recipe_id' in self.kwargs):
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
        context['product'] = Product.objects.get(id=product_id)
        return context


class CategoryView(TemplateView):
    template_name = 'category/category.html'

    def get_context_data(self, category_id, **kwargs):
        context = super().get_context_data(**kwargs)
        category = Category.objects.get(id=category_id)
        context['category'] = category
        if(self.request and self.request.user and self.request.user.is_authenticated()):
            up, created = UserPreferences.objects.get_or_create( user = self.request.user )
            context['product'] = ProductChooseAlgorithm.maximize_product_scores(up, category)
            productList = Product.objects.filter(category=category)
            for product in productList:
                score = ProductChooseAlgorithm.calculate_product_score(product, up)
                if score:
                    product.product_score = score.total()
                    product.product_score_details = str(score)
            productList = list(productList)
            productList.sort(key= lambda x: x.product_score, reverse=True)
            context['all_products'] = productList
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
        context['categories'] = Category.objects.all()
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
