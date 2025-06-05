from django.urls import path
from . import views

urlpatterns = [
    path('recipe_list/', views.recipe_list, name='recipe_list'),
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('search_recipe/', views.search_recipe, name='search_recipe')
]