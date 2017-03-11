import json

from django.utils.safestring import mark_safe
from django.views.generic import TemplateView

from questionmark import api


class QMProductsView(TemplateView):
    template_name = 'questionmark/products.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products_json = api.search_product('pindakaas')
        context['products'] = products_json['products']
        return context