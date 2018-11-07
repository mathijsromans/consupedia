from product.models import *
from django.contrib import admin


class ProductPriceInline(admin.TabularInline):
    model = ProductPrice


class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ('name', 'version', 'questionmark_id', 'brand', 'price', 'quantity', 'unit', 'food')
    inlines = [
        ProductPriceInline,
    ]


class RatingAdmin(admin.ModelAdmin):
    model = Rating
    list_display = ('user', 'product', 'rating')


class RecipeItemInline(admin.TabularInline):
    model = RecipeItem


class RecipeAdmin(admin.ModelAdmin):
    inlines = [
        RecipeItemInline,
    ]

class ProductPriceAdmin(admin.ModelAdmin):
    readonly_fields = ('datetime_created',)

admin.site.register(UserPreferences)
admin.site.register(Food)
admin.site.register(Product, ProductAdmin)
admin.site.register(Rating, RatingAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeItem)
admin.site.register(Shop)
admin.site.register(ProductPrice, ProductPriceAdmin)
admin.site.register(Certificate)
admin.site.register(ScoreTheme)
