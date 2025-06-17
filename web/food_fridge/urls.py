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
    path('food/<int:pk>/delete/', views.food_delete, name='food_delete'),
    path('map/', views.search_page, name='search_page'),       # 地圖頁面
    path('map/api/search/', views.search_api, name='search_api'),     # 搜尋 API
    path('add_food/', views.add_food, name='add_food'),  # 新增食材
    path('add_recipe/', views.add_recipe, name='add_recipe'),
    path('recipe/<int:pk>/delete/', views.recipe_delete, name='recipe_delete'),
    path('login_alert/', views.login_alert, name='login_alert'),  # 登入提示頁面
]