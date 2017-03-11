from product.models import UserPreferences, Category
from product.models import Rating
from django.contrib import admin

admin.site.register(UserPreferences)
admin.site.register(Category)
admin.site.register(Rating)
