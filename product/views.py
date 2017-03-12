import json

from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from .models import Product, Category
from .models import Rating
from .models import UserPreferences
from .productservice import ProductService, RecipeService
from .forms import ProductForm
from .forms import UserPreferenceForm
from product.algorithms import ProductChooseAlgorithm


class ProductsView(TemplateView):
    template_name = 'product/products.html'

    def get_context_data(self, **kwargs):
        if self.request.method == 'GET': # If the form is submitted
            search_query = self.request.GET.get('search_box', None)
            if search_query == 'maakrecept':
                RecipeService.create_recipe('test_recept_naam', None, 'http://test', 10, 45, 'gooi alles in de mixer, klaar', None)
        context = super().get_context_data(**kwargs)
        context['products'] = ProductService().get_all_products(search_query)
        return context

class CategoriesView(TemplateView):
    template_name = 'category/categories.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


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
            context['product'] = ProductChooseAlgorithm.return_product(up, category)
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
        up, created = UserPreferences.objects.get_or_create( user = self.request.user )
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
