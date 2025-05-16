from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search_page, name='search_page'),       # 地圖頁面
    path('api/search/', views.search_api, name='search_api'),     # 搜尋 API
]