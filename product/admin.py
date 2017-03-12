from product.models import UserPreferences, Category
from product.models import Rating
from product.models import Recipe
from product.models import Ingredient
from product.models import Product
from django.contrib import admin


class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ('name', 'price', 'amount_in_gram', 'category', 'product_score')


admin.site.register(UserPreferences)
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Rating)
admin.site.register(Recipe)
admin.site.register(Ingredient)
