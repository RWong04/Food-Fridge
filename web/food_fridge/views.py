from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Food, CustomUser
from datetime import datetime

# Create your views here.




# 新增剩食
@csrf_exempt
def create_food(request):
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
    



@csrf_exempt
def food_detail(request, food_id):

    # 更新剩食
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

    # 刪除剩食
    elif request.method == 'DELETE':
        try:
            food = Food.objects.get(pk=food_id)
            food.delete()
            return JsonResponse({'success': True})
        except Food.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Food not found'}, status=404)

    # 不支援的請求
    else:
        return JsonResponse({'success': False, 'error': 'Only PATCH or DELETE allowed'}, status=405)
