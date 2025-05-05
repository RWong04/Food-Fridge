"""Food_Waste_Fridge URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from food_fridge import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('add_food/', views.add_food),
    path('update_food/', views.update_food),
    path('delete_food/', views.delete_food),
    path('search_food/', views.search_food),
    path('check_food/', views.check_food)
]
