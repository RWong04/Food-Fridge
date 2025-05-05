from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Food, CustomUser
from datetime import datetime
from math import radians, cos, sin, asin, sqrt
from django.db.models import Q

# Create your views here.




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
def haversine(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon, dlat = lon2 - lon1, lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return 6371 * 2 * asin(sqrt(a))

# 搜尋剩食
def search_food(request):
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Only GET allowed'}, status=405)

    # 取得 query string
    keyword       = request.GET.get('keyword', '')
    user_lat      = request.GET.get('user_latitude') 
    user_lon      = request.GET.get('user_longitude')
    sort_distance = request.GET.get('sort_distance', 'false').lower() == 'true'
    sort_price    = request.GET.get('sort_price',    'false').lower() == 'true'

    # 關鍵字過濾
    qs = Food.objects.filter(
        Q(name__icontains=keyword) | Q(description__icontains=keyword)
    )

    # 轉成 tuple list
    result = []
    for f in qs:
        distance = None
        distance = haversine(float(user_lat), float(user_lon), f.latitude, f.longitude)
        result.append((
            f.pk, # food_id
            f.name,
            f.category,
            f.description,
            f.quantity,
            f.unit,
            f.price,
            f.expiration_date.isoformat(),
            f.latitude,
            f.longitude,
            f.is_soldout,
            distance                
        ))

    # 排序
    if sort_price:
        #sort by price
        result.sort(key=lambda t: t[f.price])           
    if sort_distance and user_lat and user_lon:
        # sort by distance
        result = [t for t in result if t[distance] is not None]
        result.sort(key=lambda t: t[distance])          

    return JsonResponse(result, safe=False)       

# 查看單一剩食
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

