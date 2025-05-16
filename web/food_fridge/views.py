from django.shortcuts            import render
from django.http                 import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models            import Q
from .models                     import Food
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def search(request):
    keyword = request.GET.get('simple-search')
    
    # 當 keyword 為 None 或者諏問 /all-foods/ 路徑時，返回所有食物資訊
    if keyword is None or request.path == '/all-foods/':
        try:
            foods = Food.objects.all()
            result = [{
                'id':          f.pk,
                'user':        f.user,
                'name':        f.name,
                'category':    f.category,
                'description': f.description,
                'quantity':    f.quantity,
                'unit':        f.unit,
                'price':       f.price,
                'food_address':f.food_address,
                'expiration':  f.expiration_date.isoformat(),
                'latitude':    f.latitude,
                'longitude':   f.longitude,
                'is_soldout':  f.is_soldout,
            } for f in foods]
            # 如果是 API 諏問，返回 JSON
            if request.path == '/all-foods/' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(result, safe=False)
            # 否則渲染頁面
            return render(request, 'map.html')
        except Exception as e:
            logger.exception("獲取所有食物 API 執行失敗")
            return JsonResponse(
                {'error': '獲取食物資訊發生錯誤，請稍後再試。'},
                status=500
            )
    
    # 如果前端帶了 simple-search，就當成 API 回 JSON
    try:
        # 當 keyword 為空字串時，返回所有剩食
        if keyword.strip() == '':
            foods = Food.objects.all()
        else:
            foods = Food.objects.filter(
                Q(name__icontains=keyword) |
                Q(description__icontains=keyword)
            )
        result = [{
            'id':          f.pk,
            'user':        f.user,
            'name':        f.name,
            'category':    f.category,
            'description': f.description,
            'quantity':    f.quantity,
            'unit':        f.unit,
            'price':       f.price,
            'food_address':f.food_address,
            'expiration':  f.expiration_date.isoformat(),
            'latitude':    f.latitude,
            'longitude':   f.longitude,
            'is_soldout':  f.is_soldout,
        } for f in foods]
        return JsonResponse(result, safe=False)
    except Exception as e:
        # 記錄錯誤，並回傳 500 + 錯誤訊息
        logger.exception("搜尋 API 執行失敗")
        return JsonResponse(
            {'error': '搜尋發生錯誤，請稍後再試。'},
            status=500
        )
