from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

import product.views
import questionmark.views

from website.views import ContactView
from website.views import UserPreferencesView
from website.views import UserProfileView
from website.views import MainView

# defines what view will be used to render a certain url, the views are defined in views.py
urlpatterns = [
    url(r'^$', MainView.as_view(), name='homepage'),
    url(r'^about/$', TemplateView.as_view(template_name="website/about.html"), name='about'),
    url(r'^contact/$', ContactView.as_view(), name='contact'),
    url(r'^contribute/$', TemplateView.as_view(template_name="website/contribute.html"), name='contribute'),

    url(r'^products/$', product.views.ProductsView.as_view(), name='products'),
    url(r'^product/add/$', product.views.ProductCreateView.as_view(), name='product-add'),
    url(r'^product/edit/(?P<product_id>[0-9]+)/$', product.views.ProductEditView.as_view(), name='product-edit'),
    url(r'^product/(?P<product_id>[0-9]+)/$', product.views.ProductView.as_view(), name='product'),
    url(r'^product/rating/set/?', login_required(product.views.set_product_rating)),

    url(r'^recipes/$', product.views.RecipesView.as_view(), name='recipes'),
    url(r'^recipes/add$', product.views.RecipeAddView.as_view(), name='recipe-add'),


    url(r'^categories/$', product.views.CategoriesView.as_view(), name='categories'),
    url(r'^category/(?P<category_id>[0-9]+)/$', product.views.CategoryView.as_view(), name='category'),

    url(r'^questionmark/$', questionmark.views.QMProductsView.as_view(), name='questionmark-products'),
    url(r'^user_preferences/$', product.views.UserPreferenceEditView.as_view(), name='user_prefs'),
    url(r'^what_to_eat/$', product.views.WhatToEatView.as_view(), name='what_to_eat'),
    url(r'^what_to_eat/get_result/?', product.views.get_what_to_eat_result),

    url(r'^userprofile/(?P<pk>[0-9]+)/$', login_required(UserProfileView.as_view()), name='userprofile'),

    url(r'^accounts/', include('registration.backends.simple.urls')),  # the django-registration module

    url(r'^admin/', admin.site.urls),
]


# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns += [
#         url(r'^__debug__/', include(debug_toolbar.urls)),
#     ]
