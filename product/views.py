from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.db import transaction

from .models import Product
from .productservice import ProductService
from .forms import ProductForm


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
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        return context
