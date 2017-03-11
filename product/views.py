from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.db import transaction

from .models import Product
from .models import UserPreferences
from .productservice import ProductService
from .forms import ProductForm
from .forms import UserPreferenceForm


class ProductsView(TemplateView):
    template_name = 'product/products.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = ProductService().get_all_products()
        return context


class ProductView(TemplateView):
    template_name = 'product/product.html'

    def get_context_data(self, product_id, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = Product.objects.get(id=product_id)
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
                'sustainability_weight': self.get_my_preference().sustainability_weight,
                'quality_weight': self.get_my_preference().quality_weight}

    @transaction.atomic
    def form_valid(self, form):
        userPreference = self.get_my_preference()
        userPreference.price_weight = form.cleaned_data['price_weight']
        userPreference.sustainability_weight = form.cleaned_data['sustainability_weight']
        userPreference.quality_weight = form.cleaned_data['quality_weight']
        userPreference.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['userPreference'] = self.get_my_preference()
        return context
