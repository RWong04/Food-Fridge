from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
import json
from django.views.decorators.csrf import csrf_exempt
from .models import Food, CustomUser
from datetime import datetime
from math import radians, cos, sin, asin, sqrt
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

# 新增剩食
@csrf_exempt
def add_food(request):
    if request.method == 'POST':
        try:
            # 獲取表單資料
            food_name = request.POST.get('food_name')
            food_category = request.POST.get('food_category')
            food_quantity = request.POST.get('food_quantity')
            food_expiration_date = request.POST.get('food_expired_date')
            food_address = request.POST.get('food_address')
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            food_description = request.POST.get('food_description')
            food_image = request.FILES.get('food_image')

            # 記錄接收到的數據
            logger.info(f"Received data: name={food_name}, category={food_category}, quantity={food_quantity}, "
                       f"expiration_date={food_expiration_date}, address={food_address}, "
                       f"latitude={latitude}, longitude={longitude}, description={food_description}")

            # 校驗必填項
            required_fields = [food_name, food_category, food_quantity, food_expiration_date, 
                             food_address, latitude, longitude, food_description]
            if any(field is None for field in required_fields):
                missing_fields = [field for field, value in zip(
                    ['food_name', 'food_category', 'food_quantity', 'food_expiration_date',
                     'food_address', 'latitude', 'longitude', 'food_description'],
                    required_fields) if value is None]
                error_msg = f"Missing required fields: {', '.join(missing_fields)}"
                logger.error(error_msg)
                return JsonResponse({'success': False, 'error': error_msg}, status=400)

            # 將日期轉換成日期格式
            try:
                food_expiration_date = datetime.strptime(food_expiration_date, '%Y-%m-%d').date()
            except ValueError as e:
                logger.error(f"Invalid date format: {food_expiration_date}")
                return JsonResponse({'success': False, 'error': 'Invalid date format'}, status=400)

            # 創建食物記錄
            try:
                # 暫時使用第一個用戶作為發布者
                user = CustomUser.objects.first()
                if not user:
                    logger.error("No user found in database")
                    return JsonResponse({'success': False, 'error': 'No user found'}, status=500)

                food = Food.objects.create(
                    user=user,
                    name=food_name,
                    category=food_category,
                    description=food_description,
                    quantity=float(food_quantity),
                    expiration_date=food_expiration_date,
                    latitude=float(latitude),
                    longitude=float(longitude),
                    food_address=food_address,  # 添加地址
                    unit='條',
                    price=0
                )
                logger.info(f"Successfully created food item with ID: {food.pk}")
                return JsonResponse({'success': True, 'food_id': food.id}, status=201)
            except Exception as e:
                logger.error(f"Error creating food item: {str(e)}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

        except Exception as e:
            logger.error(f"Unexpected error in add_food: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return render(request, 'new_food.html')



