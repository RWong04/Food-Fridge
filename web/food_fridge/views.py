from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm, CustomUserChangeForm, FoodForm
from django.http                 import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Food
import json
from django.db.models            import Q
import logging
from .models import Recipe, CustomUser, Ingredient, RecipeIngredient

logger = logging.getLogger(__name__)

@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        
        if form.is_valid():
            user = form.save()
            return JsonResponse({
                    "message": "Register successfully!",
                    "redirect_url": "/app/login/"
                },
                status=201
            )
        return JsonResponse(
            {
                "message": "Please fill in correctly.",
                "errors": form.errors,
                "error_code": 101
            },
            status=400
        )
    return render(request, 'register.html')

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
        except Exception:
            return JsonResponse({
                "message": "Invalid JSON.",
                "error_code": 103
            }, status=400)
        if not username or not password:
            return JsonResponse({
                "message": "Username and password required.",
                "error_code": 104
            }, status=400)
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({
                    "message": "Login successfully!",
                    "redirect_url": "/app/profile/"
                }, status=201)
        else:
            return JsonResponse({
                "message": "帳號或密碼錯誤！",
                "error_code": 101
            }, status=400)
    return render(request, "login.html")

@csrf_exempt
@login_required
def profile_view(request):
    user = request.user
    foods = user.foods.all()
    return render(request, 'profile.html', {'user': user, 'foods': foods})

@csrf_exempt
@login_required
def profile_edit_view(request):
    user = request.user
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return JsonResponse({
                    "message": "Profile updated successfully!",
                    "redirect_url": "/app/profile/"
                }, status=201)
        return JsonResponse({"errors": form.errors}, status=400)
    else:
        form = CustomUserChangeForm(instance=user)
    return render(request, 'profile_edit.html', {'form': form})

@csrf_exempt
@login_required
def food_edit_view(request, pk):
    food = get_object_or_404(Food, pk=pk, user=request.user)
    if request.method == 'POST':
        form = FoodForm(request.POST, instance=food)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = FoodForm(instance=food)
    return render(request, 'food_edit.html', {'form': form, 'food': food})



@csrf_exempt
def search_page(request):
    # 回傳地圖 HTML 頁面
    return render(request, 'map.html')

@csrf_exempt
def search_api(request):
    if request.method == 'GET':
        search_term = request.GET.get('simple-search', None)

        if search_term:
            foods = Food.objects.filter(
                Q(name__icontains=search_term) |
                Q(description__icontains=search_term)
            )
        else:
            foods = Food.objects.all()

        result = [{
            'id': f.pk,
            'user': str(f.user),
            'name': f.name,
            'category': f.category,
            'description': f.description,
            'quantity': f.quantity,
            'unit': f.unit,
            'price': f.price,
            'food_address': f.food_address,
            'expiration': f.expiration_date.isoformat() if f.expiration_date else None,
            'latitude': float(f.latitude) if f.latitude is not None else None, # 確保是 float
            'longitude': float(f.longitude) if f.longitude is not None else None, # 確保是 float
            'is_soldout': f.is_soldout,
        } for f in foods]

        return JsonResponse(result, safe=False)
    else:
        return HttpResponse(status=405, reason='Method Not Allowed')
    
@csrf_exempt
def add_food(request):
    if request.method == 'POST':
        try:
            # 獲取表單資料
            food_name = request.POST.get('food_name')
            food_category = request.POST.get('food_category')
            food_quantity = request.POST.get('food_quantity')
            food_unit = request.POST.get('food_unit')
            food_price = request.POST.get('food_price')
            food_expiration_date = request.POST.get('food_expired_date')
            food_address = request.POST.get('food_address')
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            food_description = request.POST.get('food_description', '')
            food_image = request.FILES.get('food_image')

            # 記錄接收到的數據
            logger.info(f"Received data: name={food_name}, category={food_category}, quantity={food_quantity}, "
                       f"unit={food_unit}, price={food_price}, "
                       f"expiration_date={food_expiration_date}, address={food_address}, "
                       f"latitude={latitude}, longitude={longitude}, description={food_description}, "
                       f"image={food_image.name if food_image else None}")

            # 校驗必填項
            required_fields = {'food_name': food_name, 'food_category': food_category, 
                              'food_quantity': food_quantity, 'food_unit': food_unit, 'food_price': food_price,
                              'food_expired_date': food_expiration_date,
                              'food_address': food_address, 'latitude': latitude, 'longitude': longitude}
            
            missing_fields = [field for field, value in required_fields.items() if not value]
            if missing_fields:
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

                # 處理數值轉換
                try:
                    quantity = float(food_quantity)
                    lat = float(latitude) if latitude else 0
                    lng = float(longitude) if longitude else 0
                except ValueError:
                    return JsonResponse({'success': False, 'error': 'Invalid numeric values'}, status=400)

                # 創建食物記錄
                food = Food.objects.create(
                    user=user,
                    name=food_name,
                    category=int(food_category),
                    description=food_description,
                    quantity=quantity,
                    unit =food_unit,
                    price=float(food_price),
                    expiration_date=food_expiration_date,
                    img_path=food_image,  # 如果沒有上傳圖片，這裡會是None
                    latitude=lat,
                    longitude=lng,
                    food_address=food_address
                )
                
                logger.info(f"Successfully created food item with ID: {food.pk}")
                return JsonResponse({
                    'success': True, 
                    'food_id': food.id, 
                    "redirect_url": "/app/profile/"
                }, status=201, )
            except Exception as e:
                logger.error(f"Error creating food item: {str(e)}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

        except Exception as e:
            logger.error(f"Unexpected error in add_food: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return render(request, 'new_food.html')

@csrf_exempt
def add_recipe(request):
    
    if request.method == 'POST':
        try:
            # 獲取表單資料
            name = request.POST.get('recipe_name')
            description = request.POST.get('recipe_description')
            
            if not name:
                return JsonResponse({'success': False, 'error': 'Recipe name is required'}, status=400)

            # 暫時使用第一個用戶作為發布者
            user = CustomUser.objects.first()
            if not user:
                return JsonResponse({'success': False, 'error': 'No user found'}, status=400)

            # 創建食譜
            recipe = Recipe.objects.create(
                user=user,
                name=name,
                description=description,
            )
            
            # 處理食材數據
            ingredient_index = 0
            while ingredient_index < 10:  # 檢查最多10個食材欄位
                ingredient_name = request.POST.get(f'ingredient_name_{ingredient_index}')
                ingredient_quantity = request.POST.get(f'ingredient_quantity_{ingredient_index}')
                ingredient_unit = request.POST.get(f'ingredient_unit_{ingredient_index}')
                
                # 如果找不到這個索引的食材名稱，跳出循環
                if ingredient_name is None:
                    ingredient_index += 1
                    continue
                
                # 只有當食材名稱不為空時才處理
                if ingredient_name and ingredient_name.strip():
                    # 檢查數量是否有效
                    try:
                        quantity = float(ingredient_quantity) if ingredient_quantity else 0
                        if quantity <= 0:
                            ingredient_index += 1
                            continue  # 跳過數量無效的食材
                    except (ValueError, TypeError):
                        ingredient_index += 1
                        continue  # 跳過數量無效的食材
                    
                    # 單位預設值
                    unit = ingredient_unit.strip() if ingredient_unit else '份'
                    
                    # 獲取或創建食材
                    ingredient, created = Ingredient.objects.get_or_create(
                        name=ingredient_name.strip()
                    )
                    
                    # 創建食譜-食材關聯
                    RecipeIngredient.objects.create(
                        recipe=recipe,
                        ingredient=ingredient,
                        quantity=quantity,
                        unit=unit
                    )
                
                ingredient_index += 1
                
            return JsonResponse({'success': True, 'recipe_id': recipe.id}, status=201)
            
        except Exception as e:
            logger.error(f"Error creating recipe: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return render(request, 'add_recipe.html')

@login_required
def food_delete(request, pk):
    if request.method == "POST":
        food = get_object_or_404(Food, pk=pk, user=request.user)
        food.delete()
    return redirect('profile') 