from django.urls import path
from . import views

urlpatterns = [
    path('add_food/', views.add_food),
    # 其他 URL 模式
    # path('update_food/<int:food_id>/', views.update_food),
    # path('delete_food/<int:food_id>/', views.delete_food),
    # path('search/', views.search),
    # path('check_food/<int:food_id>/', views.check_food),
]