from django.urls import path
from . import views

urlpatterns = [
    path('search_food/', views.search_food, name='search_food'),
    path('search/', views.search),
]