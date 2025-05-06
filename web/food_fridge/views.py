from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
import json
from django.views.decorators.csrf import csrf_exempt
from .models import Food, CustomUser
from datetime import datetime
from math import radians, cos, sin, asin, sqrt
from django.db.models import Q

def new_food(request):
  template = loader.get_template('new_food.html')
  return HttpResponse(template.render())


# 新增剩食
@csrf_exempt
def add_food(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Only POST allowed'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    
    # 傳入參數
    required_fields = [
        'user_id', 'name', 'category', 'description',
        'quantity', 'expiration_date', 'latitude', 'longitude'
    ]

    #如果沒填好會擋
    for field in required_fields:
        if field not in data:
            return JsonResponse({'success': False, 'error': f'Missing field: {field}'}, status=400)

    try:
        # 從個資抓使用者id
        user = CustomUser.objects.get(id=data['user_id'])

        food = Food.objects.create(
            user = user,
            name = data['name'],
            category = data['category'],
            description = data['description'],
            quantity = float(data['quantity']),
            expiration_date = datetime.strptime(data['expiration_date'], '%Y-%m-%d').date(),
            latitude = float(data['latitude']),
            longitude = float(data['longitude']),
            # 這邊是預設補值
            unit='條',
            price=0  # 假設沒收價格預設為 0
        )
        return JsonResponse({'success': True, 'food_id': food.id}, status=201)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    



# 更新剩食
@csrf_exempt
def update_food(request, food_id):
    if request.method == 'PATCH':
        try:
            data = json.loads(request.body.decode('utf-8'))
            food = Food.objects.get(pk=food_id)
            for field in ['name', 'category', 'description', 'quantity', 'unit', 'price', 'expiration_date', 'latitude', 'longitude', 'is_soldout']:
                if field in data:
                    setattr(food, field, data[field])
            food.save()
            return JsonResponse({'success': True})
        except Food.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Food not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        
    return JsonResponse({'success': False, 'error': 'Only PATCH allowed'}, status=405)
    # 刪除剩食
@csrf_exempt
def delete_food(request, food_id):
    if request.method == 'DELETE':
        try:
            food = Food.objects.get(pk=food_id)
            food.delete()
            return JsonResponse({'success': True})
        except Food.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Food not found'}, status=404)

    
    return JsonResponse({'success': False, 'error': 'Only DELETE allowed'}, status=405)
    


# --- 工具：計算兩座標直線距離（公里） ---
   

# 搜尋剩食
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

# 查看單一剩食
@csrf_exempt
def check_food(request, food_id):
    if request.method == 'GET':
        try:
            f = Food.objects.get(pk=food_id)
            data = (
                f.pk,
                f.name,
                f.category,
                f.description,
                f.quantity,
                f.unit,
                f.price,
                f.expiration_date.isoformat(),
                f.latitude,
                f.longitude,
                f.is_soldout
            )
            return JsonResponse(data, safe=False)     # tuple -> JSON array
        except Food.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Food not found'}, status=404)
    return JsonResponse({'success': False, 'error': 'Only GET allowed'}, status=405)