from django.shortcuts import render
from django.http import JsonResponse
from django.template import loader
import json
from django.views.decorators.csrf import csrf_exempt
from .models import Recipe, CustomUser
from datetime import datetime
from django.db.models import Q


@csrf_exempt
def add_recipe(request):
    """
    新增食譜 API: 接收 POST 請求，新增一筆食譜資料到資料庫。

    請求方式：
        POST

    請求參數(form-data):
        - recipe_name: 食譜名稱（必填）
        - recipe_description: 食譜描述（選填）

    回應格式(JSON):
        成功：
            {
                "success": true,
                "recipe_id": <新食譜ID>
            }
        失敗：
            {
                "success": false,
                "error": <錯誤訊息>
            }

    Status Code 說明：
        - 201: 建立成功
        - 400: 請求參數錯誤(如缺少名稱或找不到用戶)
        - 500: 伺服器內部錯誤
    """

    if request.method == 'POST':
        try:
            # 獲取表單資料
            name = request.POST.get('recipe_name')
            description = request.POST.get('recipe_description')
            # 因為 models.py 已有 auto_now_add=True，所以不用輸入
            if not name:
                return JsonResponse({'success': False, 'error': 'Recipe name id required'}, status=400)

            # 暫時使用第一個用戶作為發布者
            user = CustomUser.objects.first()
            if not user:
                return JsonResponse({'success': False, 'error': 'No user found'}, status=400)


            # 把食譜加到資料庫
            recipe = Recipe.objects.create(
                user=user,
                name=name,
                description=description,
            )
                
            return JsonResponse({'success': True, 'recipe_id': recipe.id}, status=201)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


    return render(request, 'add_recipe.html')


