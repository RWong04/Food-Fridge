from django.shortcuts import render

# Create your views here.

def recipe_list(request):
    # 回傳地圖 HTML 頁面
    return render(request, 'search_recipe.html')