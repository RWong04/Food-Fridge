from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Food
from django.db.models import Q

def search_food(request):
  template = loader.get_template('map.html')
  return HttpResponse(template.render())

@csrf_exempt
def search(request):
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Only GET allowed'}, status=405)

    # 從請求中獲取搜尋參數
    keyword = request.GET.get('simple-search', '')
    
    # 根據關鍵字過濾
    foods = Food.objects.filter(
        Q(name__icontains = keyword) | Q(description__icontains = keyword)
    )

    result = []
    for food in foods:
        # distance = None
        # if user_lat and user_lon:
        #     # 計算距離
        #     distance = haversine(float(user_lat), float(user_lon), food.latitude, food.longitude)
        result.append((
            food.pk,               # food_id
            food.name,
            food.category,
            food.description,
            food.quantity,
            food.unit,
            food.price,
            food.expiration_date.isoformat(),
            food.latitude,
            food.longitude,
            food.is_soldout,
            # distance                # 顯示距離
        ))

    

    return JsonResponse(result, safe=False)  # 回傳符合條件的剩食     

