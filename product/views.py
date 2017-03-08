from django.shortcuts import render
from django.views.generic import TemplateView

from product.models import Product


class ProductsView(TemplateView):
    template_name = 'product/products.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        return context


class ProductView(TemplateView):
    template_name = 'product/product.html'

    def get_context_data(self, id, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = Product.objects.get(id=id)
        return context
