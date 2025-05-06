from django.urls import path
from . import views

urlpatterns = [
    path('new_food/', views.new_food, name='new_food'),
    path('add_food/', views.add_food),
    path('update_food/', views.update_food),
    path('delete_food/', views.delete_food),
    path('search/', views.search),
    path('check_food/', views.check_food)
]