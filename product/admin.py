from django.contrib import admin

from product.models import Product
from product.models import Revision
from product.models import ProductName, Price


class PriceInline(admin.TabularInline):
    extra = 1
    model = Price


class ProductNameInline(admin.TabularInline):
    extra = 1
    model = ProductName


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    inlines = [
        PriceInline,
        ProductNameInline,
    ]


admin.site.register(Product, ProductAdmin)
admin.site.register(Revision)
