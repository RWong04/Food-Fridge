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
    # 如果前端帶了 simple-search，就當成 API 回 JSON
    if keyword is not None:
        try:
            foods = Food.objects.filter(
                Q(name__icontains=keyword) |
                Q(description__icontains=keyword)
            )
            result = [{
                'id':          f.pk,
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

    # 沒帶參數就回地圖頁面
    try:
        return render(request, 'map.html')
    except Exception as e:
        logger.exception("地圖頁面渲染失敗")
        return HttpResponse(
            "無法顯示地圖，請稍後再試。",
            status=500
        )
