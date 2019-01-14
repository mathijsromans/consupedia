from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

import product.views

from website.views import ContactView
from website.views import UserProfileView
from website.views import MainView

# defines what view will be used to render a certain url, the views are defined in views.py
urlpatterns = [
    url(r'^$', MainView.as_view(), name='homepage'),
    url(r'^about/$', TemplateView.as_view(template_name="website/about.html"), name='about'),
    url(r'^contact/$', ContactView.as_view(), name='contact'),

    url(r'^products/$', product.views.ProductsView.as_view(), name='products'),
    url(r'^product/add/$', product.views.ProductCreateView.as_view(), name='product-add'),
    url(r'^product/edit/(?P<product_id>[0-9]+)/$', product.views.ProductEditView.as_view(), name='product-edit'),
    url(r'^product/(?P<product_id>[0-9]+)/$', product.views.ProductView.as_view(), name='product'),
    url(r'^product/rating/set/?', login_required(product.views.set_product_rating)),
    url(r'^product/price/add/$', product.views.PriceCreateView.as_view(), name='price-add'),

    url(r'^recipes/$', product.views.RecipesView.as_view(), name='recipes'),
    url(r'^recipe/(?P<recipe_id>[0-9]+)/$', product.views.RecipeDetailView.as_view(), name='recipe_detail'),
    url(r'^recursive/(?P<recipe_id>[0-9]+)/$', product.views.RecursiveRecipeView.as_view(), name='recursive_recipe'),
    url(r'^recipes/new$', product.views.create_new_recipe, name='recipe-new'),
    url(r'^recipes/new/ah$', product.views.RecipeAHAddView.as_view(), name='recipe-new-ah'),
    url(r'^recipes/edit/(?P<recipe_id>[0-9]+)/$', product.views.RecipeEditView.as_view(), name='recipe-edit'),
    url(r'^recipes/edit/items/(?P<recipe_id>[0-9]+)/$', product.views.RecipeEditItemsView.as_view(), name='recipe-edit-items'),
    url(r'^recipes/edit/new/(?P<recipe_id>[0-9]+)/(?P<foods_created>.*)/&', product.views.RecipeEditNewView.as_view(), name='recipe-edit-new'),
    url(r'^recipes/ingredient/edit/(?P<recipe_item_id>[0-9]+)/$', product.views.RecipeItemEditView.as_view(), name='recipe_item-edit'),
    url(r'^recipes/ingredient/add/(?P<recipe_id>[0-9]+)/$', product.views.add_recipe_item, name='recipe_item-add'),

    url(r'^foods/$', product.views.FoodsView.as_view(), name='foods'),
    url(r'^food/(?P<food_id>[0-9]+)/$', product.views.FoodView.as_view(), name='food'),
    url(r'^food/edit/(?P<food_id>[0-9]+)/$', product.views.FoodEditView.as_view(), name='food-edit'),
    url(r'^food/remove/(?P<food_id>[0-9]+)/$', product.views.FoodRemoveView.as_view(), name='food-remove'),
    url(r'^food/product/remove/$', product.views.remove_food_product),
    url(r'^food/products/edit/(?P<food_id>[0-9]+)/$', product.views.FoodProductsEditView.as_view(), name='food-products-edit'),
    url(r'^food/products/update/(?P<food_id>[0-9]+)/$', product.views.update_food_products, name='food-products-update'),

    url(r'^contribute/$', TemplateView.as_view(template_name="website/contribute.html"), name='contribute'),
    url(r'^contribute/incomplete/$', product.views.IncompleteView.as_view(), name='incomplete'),
    url(r'^contribute/foods/$', product.views.ContributeFoodsView.as_view(), name='contribute-foods'),
    url(r'^contribute/foods/no_recipe/$', product.views.ContributeFoodsWithoutRecipeView.as_view(), name='contribute-food-without-recipes'),
    url(r'^contribute/scs/$', product.views.ContributeScoreCreatorsView.as_view(), name='contribute-scs'),
    url(r'^contribute/sc/(?P<sc_id>[0-9]+)/$', product.views.ScoreCreatorEditView.as_view(), name='contribute-sc'),
    url(r'^contribute/sc/add/$', product.views.ScoreCreatorCreateView.as_view(), name='sc-add'),
    url(r'^contribute/rankings/$', product.views.ContributeRankingsView.as_view(), name='contribute-rankings'),

    url(r'^user_preferences/$', product.views.UserPreferenceEditView.as_view(), name='user_prefs'),
    url(r'^user_preferences/supply/add$', product.views.SupplyNewView.as_view(), name='supply-add'),
    url(r'^user_preference/set/?', login_required(product.views.set_user_preference_data)),
    url(r'^what_to_eat/$', product.views.WhatToEatView.as_view(), name='what_to_eat'),
    url(r'^what_to_eat/get_result/?', product.views.get_what_to_eat_result),

    url(r'^userprofile/(?P<pk>[0-9]+)/$', login_required(UserProfileView.as_view()), name='userprofile'),

    url(r'^accounts/', include('registration.backends.simple.urls')),  # the django-registration module

    url(r'^recipes/get_for_user', login_required(product.views.get_recipes_for_user)),

    url(r'^questionnaire/$', TemplateView.as_view(template_name="website/questionnaire.html"), name='questionnaire'),

    url(r'^admin/', admin.site.urls),
]


# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns += [
#         url(r'^__debug__/', include(debug_toolbar.urls)),
#     ]
