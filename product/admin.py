from product.models import UserPreferences, Category
from product.models import Rating
from product.models import Recipe
from product.models import Shop
from product.models import ProductPrice
from product.models import Ingredient
from product.models import Product
from django.contrib import admin


class ProductPriceInline(admin.TabularInline):
    model = ProductPrice


class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ('name', 'version', 'questionmark_id', 'brand', 'price', 'quantity', 'unit', 'category', 'product_score')
    inlines = [
        ProductPriceInline,
    ]


class RatingAdmin(admin.ModelAdmin):
    model = Rating
    list_display = ('user', 'product', 'rating')


class IngredientInline(admin.TabularInline):
    model = Ingredient


class RecipeAdmin(admin.ModelAdmin):
    inlines = [
        IngredientInline,
    ]


admin.site.register(UserPreferences)
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Rating, RatingAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient)
admin.site.register(Shop)
admin.site.register(ProductPrice)
