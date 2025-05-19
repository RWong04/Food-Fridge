# urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('add_recipe/', views.add_recipe, name='addRecipe'),
]