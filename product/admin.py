from django.contrib import admin

from product.models import Product
from product.models import ProductName, Price


class PriceInline(admin.TabularInline):
    max_num = 1
    model = Price


class ProductNameInline(admin.TabularInline):
    max_num = 1
    model = ProductName


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    inlines = [
        PriceInline,
        ProductNameInline,
    ]


admin.site.register(Product, ProductAdmin)
