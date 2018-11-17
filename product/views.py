import json
import logging
from django.db.models import Q
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from .models import *
from .productservice import RecipeService
from . import forms
from product.productservice import ProductService

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


class FoodsView(TemplateView):
    template_name = 'food/foods.html'

    def dispatch(self, request, *args, **kwargs):
        create_query = self.request.GET.get('create_box', None)
        if create_query:
            food, created = Food.objects.get_or_create(name=create_query)
            if self.request.GET.get('create_new_with_products'):
                ProductService.update_products(food)
                return redirect(reverse('food-products-edit', args=(food.id,)))
            return redirect(reverse('foods'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['foods'] = Food.objects.all().order_by('name')
        return context


class RecipesView(TemplateView):
    template_name = 'recipe/recipe_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipes = Recipe.objects.all()
        context['recipes'] = recipes
        return context


def calculateTotalScore(recipe, up):
    scores = recipe.score(up)
    return scores
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
        up, created = UserPreferences.objects.get_or_create(user=self.request.user)
        context['recipe'] = recipe
        context['food_quantity_scores'] = recipe.food_quantity_scores(up)
        context['score'] = recipe.score(up)
        context['preparation'] = recipe.preparation
        return context


class RecursiveRecipeView(TemplateView):
    template_name = 'recipe/recursive_recipe_show.html'

    def get_context_data(self, recipe_id, **kwargs):
        context = super().get_context_data(**kwargs)
        recipe = Recipe.objects.get(id=recipe_id)
        up, created = UserPreferences.objects.get_or_create(user=self.request.user)
        context['recipe'] = recipe
        context['food_quantity_scores'] = recipe.recursive_food_quantity_scores(up)
        context['score'] = recipe.score(up)
        context['preparation'] = recipe.recursive_preparation(up)
        return context


def create_new_recipe(request):
    template_name = 'recipe/recipe_new.html'
    if request.method == 'GET':
        formset = forms.RecipeItemFormset(request.GET or None)
        recipe_form = forms.RecipeForm(request.GET or None)
    elif request.method == 'POST':
        formset = forms.RecipeItemFormset(request.POST)
        recipe_form = forms.RecipeForm(request.POST)
        if formset.is_valid() and recipe_form.is_valid():
            name = recipe_form.cleaned_data.get('name')
            provides = recipe_form.cleaned_data.get('provides')
            quantity = recipe_form.cleaned_data.get('quantity')
            source_if_not_user = recipe_form.cleaned_data.get('source_if_not_user')
            preparation_time_in_min = recipe_form.cleaned_data.get('preparation_time_in_min')
            preparation = recipe_form.cleaned_data.get('preparation')
            recipe = Recipe.objects.create(name=name,
                                           provides=provides,
                                           quantity=quantity,
                                           source_if_not_user=source_if_not_user,
                                           preparation_time_in_min=preparation_time_in_min,
                                           preparation=preparation)
            for form in formset:
                quantity = form.cleaned_data.get('quantity')
                food = form.cleaned_data.get('food')
                if quantity:
                    RecipeItem.objects.create(quantity=quantity, food=food, recipe=recipe)
            return redirect('recipes')
    return render(request, template_name, {
        'formset': formset,
        'recipe_form': recipe_form
    })


class RecipeAHAddView(FormView):
    template_name = 'recipe/recipe_new_ah.html'
    form_class = forms.RecipeURLForm
    success_url = '/recipes/'

    def get_initial(self, **kwargs):
        return {'url': 'R-R399568',
                'quantity': 1}

    def get_context_data(self, **kwargs):
        if not Food.objects.exists():
            Food.objects.create(name='Warme maaltijd')
        context = super().get_context_data(**kwargs)
        return context

    @transaction.atomic
    def form_valid(self, form):
        recipe, foods_created = RecipeService.create_recipe_from_ah_id(
            form.cleaned_data['url'],
            form.cleaned_data['provides'],
            form.cleaned_data['quantity'])
        logger.info('CREATED RECIPE ' + str(recipe))
        foods_created = list(recipe.recipeitem_set.values_list('food_id', flat=True))
        recipe_id = recipe.id if recipe else 0
        return redirect(reverse('recipe-edit-new', args=[recipe_id, json.dumps(foods_created)]))


class RecipeEditNewView(TemplateView):
    template_name = 'recipe/recipe_edit_new.html'

    def get_context_data(self, recipe_id, foods_created, **kwargs):
        foods_created = json.loads(foods_created)
        context = super().get_context_data()
        context['recipe'] = Recipe.objects.get(id=recipe_id)
        context['foods_created'] = Food.objects.filter(id__in=foods_created) if foods_created is not None else None
        return context


class RecipeEditView(TemplateView):
    template_name = 'recipe/recipe_edit.html'

    def get_context_data(self, recipe_id, **kwargs):
        context = super().get_context_data(**kwargs)
        recipe = Recipe.objects.get(id=recipe_id)
        up, created = UserPreferences.objects.get_or_create(user=self.request.user)
        recipe_items_and_scores = [(recipe_item, recipe_item.score(up)) for recipe_item in recipe.recipeitem_set.all()]
        context['recipe'] = recipe
        context['recipe_items_and_scores'] = recipe_items_and_scores
        return context


class ProductView(TemplateView):
    template_name = 'product/product_page.html'

    def get_context_data(self, product_id, **kwargs):
        context = super().get_context_data(**kwargs)
        product = Product.objects.get(id=product_id)
        up, created = UserPreferences.objects.get_or_create(user=self.request.user)
        score = product.score(up)
        context['product'] = product
        context['score'] = score
        return context


class FoodProductsEditView(TemplateView):
    template_name = 'food/food_products_edit.html'

    def get_context_data(self, food_id, **kwargs):
        food = Food.objects.get(id=food_id)
        context = super().get_context_data(**kwargs)
        context['food'] = food
        if self.request.user.is_authenticated():
            up, created = UserPreferences.objects.get_or_create(user=self.request.user)
            products_and_scores = food.recommended_products_and_scores(up)
            context['products_and_total_scores'] = [(p[0], p[1].total()) for p in products_and_scores]
        return context


class FoodView(TemplateView):
    template_name = 'food/food.html'

    def get_context_data(self, food_id, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            food = Food.objects.get(id=food_id)
            context['food'] = food
            context['conversions'] = food.conversion_set.all()
            if self.request.user.is_authenticated():
                up, created = UserPreferences.objects.get_or_create(user=self.request.user)
                products_and_scores = food.recommended_products_and_scores(up)
                recipes_and_scores = food.recommended_recipes_and_scores(up)
                recommended_product = None
                recommended_recipe = None
                score = None
                if products_and_scores:
                    recommended_product = products_and_scores[0][0]
                    score = products_and_scores[0][1]
                if recipes_and_scores:
                    recommended_recipe_score = recipes_and_scores[0][1]
                    if not score or recommended_recipe_score < score:
                        recommended_recipe = recipes_and_scores[0][0]
                        score = recommended_recipe_score
                context['products_and_total_scores'] = [(p[0], p[1].total()) for p in products_and_scores]
                context['recipes_with_info'] = [(p[0], p[1].price(), p[1].total()) for p in recipes_and_scores]
                prs = food.recommended_product_recipe_score(up)
                context['recommended_product'] = prs.product
                context['recommended_recipe'] = prs.recipe
                context['score'] = score
                if food.unit == 'g':
                    context['kg_price'] = score.price()*1000
        except ObjectDoesNotExist:
            pass
        return context


def remove_food_product(request):
    Product.objects.get(id=int(request.POST['product_id'])).delete()
    response = json.dumps({'status': 'success'})
    return HttpResponse(response, content_type='application/json')


class ProductCreateView(FormView):
    template_name = 'product/product_add.html'
    form_class = forms.ProductForm
    success_url = '/products/'

    @transaction.atomic
    def form_valid(self, form):
        Product.objects.create(name=form.cleaned_data['name'], price=form.cleaned_data['price'])
        return super().form_valid(form)


class ProductEditView(FormView):
    template_name = 'product/product_edit.html'
    form_class = forms.ProductForm
    success_url = '/'

    @property
    def product(self):
        return Product.objects.get(id=self.kwargs['product_id'])

    def get_initial(self):
        return {'food': self.product.food}

    @transaction.atomic
    def form_valid(self, form):
        product = self.product
        product.food = form.cleaned_data['food']
        product.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        return context


class RecipeItemEditView(FormView):
    template_name = 'recipe/recipe_item_edit.html'
    form_class = forms.RecipeItemForm

    @property
    def success_url(self):
        return '/recipe/' + str(self.recipe_item.recipe.id)

    @property
    def recipe_item(self):
        return RecipeItem.objects.get(id=self.kwargs['recipe_item_id'])

    def get_initial(self):
        recipe_item = self.recipe_item
        return {'quantity': recipe_item.quantity,
                'food': recipe_item.food}

    @transaction.atomic
    def form_valid(self, form):
        recipe_item = self.recipe_item
        recipe_item.quantity = form.cleaned_data['quantity']
        recipe_item.food = form.cleaned_data['food']
        recipe_item.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recipe_item'] = self.recipe_item
        return context


def add_recipe_item(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    food = ProductService.get_or_create_unknown_food()
    recipe_item = RecipeItem.objects.create(quantity=1, food=food, recipe=recipe)
    return redirect(reverse('recipe_item-edit', args=(recipe_item.id,)))


class FoodContributeEditView(FormView):
    template_name = 'contribute/food_edit.html'
    form_class = forms.FoodForm

    @property
    def success_url(self):
        return '/contribute/'

    @property
    def food(self):
        return Food.objects.get(id=self.kwargs['food_id'])

    def get_initial(self):
        food = self.food
        return {'name': food.name,
                'unit': food.unit,
                'score_creator': food.score_creator}

    @transaction.atomic
    def form_valid(self, form):
        food = self.food
        food.name = form.cleaned_data['name']
        food.unit = form.cleaned_data['unit']
        food.equiv_weight = form.cleaned_data['equiv_weight']
        food.score_creator = form.cleaned_data['score_creator']
        food.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['food'] = self.food
        return context


class FoodEditView(FormView):
    template_name = 'food/food_edit.html'
    form_class = forms.FoodForm

    @property
    def success_url(self):
        return '/food/' + str(self.food.id)

    @property
    def food(self):
        return Food.objects.get(id=self.kwargs['food_id'])

    def get_initial(self):
        food = self.food
        return {'name': food.name,
                'unit': food.unit}

    @transaction.atomic
    def form_valid(self, form):
        food = self.food
        food.name = form.cleaned_data['name']
        food.unit = form.cleaned_data['unit']
        food.equiv_weight = form.cleaned_data['equiv_weight']
        food.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['food'] = self.food
        return context


class UserPreferenceEditView(FormView):
    template_name = 'user/user_preference_edit.html'
    form_class = forms.UserPreferenceForm
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


class IncompleteView(TemplateView):
    template_name = 'contribute/incomplete.html'

    def get_context_data(self, **kwargs):
        default = ScoreCreator.objects.get(name='default')
        context = super().get_context_data(**kwargs)
        context['foods'] = Food.objects.filter(Q(score_creator=default) | Q(score_creator=None)).order_by('name')
        return context


class ContributeFoodsView(TemplateView):
    template_name = 'contribute/foods.html'

    def get_context_data(self, **kwargs):
        default = ScoreCreator.objects.get(name='default')
        context = super().get_context_data(**kwargs)
        context['foods'] = Food.objects.all().order_by('name')
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
    food = Food.objects.get(id=request.POST['food_id'])
    up = UserPreferences()
    #TODO: get user preferences from post request.
    up.price_weight = 5
    up.environment_weight = 5
    up.social_weight = 5
    up.animals_weight = 5
    up.personal_health_weight = 5
    result = None  # TODO: get product
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