from django.urls import path
from . import views

urlpatterns = [
    path('new_food/', views.new_food, name='new_food'),
]