from product.models import UserPreferences, Category
from product.models import Rating
from product.models import Product
from django.contrib import admin

admin.site.register(UserPreferences)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Rating)
