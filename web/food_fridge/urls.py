# urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/', views.profile_view, name='profile'),
    path('food/<int:pk>/edit/', views.food_edit_view, name='food_edit'),
]