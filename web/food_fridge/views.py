from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm, CustomUserChangeForm, FoodForm
from django.http                 import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Food, Meetup, Message
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
                "message": "格式不符，請聯絡管理員",
                "error_code": 103
            }, status=400)
        if not username or not password:
            return JsonResponse({
                "message": "帳號密碼不得為空！",
                "error_code": 104
            }, status=400)
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({
                    "message": "成功登入！",
                    "redirect_url": "/app/profile/"
                }, status=201)
        else:
            return JsonResponse({
                "message": "帳號或密碼錯誤！",
                "error_code": 101
            }, status=400)
    return render(request, "login.html")

@csrf_exempt
@login_required(login_url='/app/login_alert/')
def profile_view(request):
    user = request.user
    foods = user.foods.all()
    recipes = user.recipes.all()
    return render(request, 'profile.html', {'user': user, 'foods': foods, 'recipes': recipes})

def login_alert(request):
    return render(request, 'login_alert.html')
@csrf_exempt
@login_required(login_url='/app/login_alert/')
def profile_edit_view(request):
    user = request.user
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return JsonResponse({
                    "message": "更新個人檔案成功！",
                    "redirect_url": "/app/profile/"
                }, status=201)
        return JsonResponse({"errors": form.errors}, status=400)
    else:
        form = CustomUserChangeForm(instance=user)
    return render(request, 'profile_edit.html', {'form': form})

@csrf_exempt
@login_required(login_url='/app/login_alert/')
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
def recipe_list(request):
    # 獲取所有食譜
    recipes = Recipe.objects.all()
    
    # 將食譜資料轉換為 JSON 格式
    recipes_data = []
    for recipe in recipes:
        # 獲取該食譜的所有食材
        ingredients = RecipeIngredient.objects.filter(recipe=recipe)
        ingredients_data = [
            {
                'name': ingredient.ingredient.name,
                'quantity': ingredient.quantity,
                'unit': ingredient.unit
            }
            for ingredient in ingredients
        ]
        
        recipe_data = {
            'id': recipe.id,
            'name': recipe.name,
            'description': recipe.description,
            'create_time': recipe.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'user': recipe.user.username,
            'ingredients': ingredients_data
        }
        recipes_data.append(recipe_data)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # 如果是 AJAX 請求，返回 JSON 數據
        return JsonResponse({'recipes': recipes_data})
    
    # 如果是普通請求，返回頁面
    return render(request, 'search_recipe.html', {'recipes': recipes_data})

@csrf_exempt
def search_recipe(request):
    if request.method == 'GET':
        search_term = request.GET.get('simple-search', '')

        recipes = Recipe.objects.filter(
            Q(name__icontains=search_term) |
            Q(description__icontains=search_term) |
            Q(recipe_ingredients__ingredient__name__icontains=search_term)
        ).distinct()

        result = []
        for recipe in recipes:
            ingredients = RecipeIngredient.objects.filter(recipe=recipe)
            ingredients_data = [
                {
                    'name': ingredient.ingredient.name,
                    'quantity': ingredient.quantity,
                    'unit': ingredient.unit
                }
                for ingredient in ingredients
            ]
            recipe_data = {
                'id': recipe.id,
                'name': recipe.name,
                'description': recipe.description,
                'create_time': recipe.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                'user': str(recipe.user),
                'ingredients': ingredients_data
            }
            result.append(recipe_data)

        # 如果是 AJAX 請求就回傳 JSON
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(result, safe=False)

        # 否則回傳 HTML 頁面
        return render(request, 'search_recipe.html', {
            'recipes': result,
            'query': search_term
        })

    return HttpResponse(status=405, reason='Method Not Allowed')

def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    ingredients = RecipeIngredient.objects.filter(recipe=recipe)
    
    context = {
        'recipe': recipe,
        'ingredients': ingredients,
    }
    
    return render(request, 'recipe_detail.html', context)

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
@login_required(login_url='/app/login_alert/')
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
                user = request.user
                if not user or not user.is_authenticated:
                    return JsonResponse({'success': False, 'error': 'No user found'}, status=400)

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
@login_required(login_url='/app/login_alert/')
def add_recipe(request):
    
    if request.method == 'POST':
        try:
            # 獲取表單資料
            name = request.POST.get('recipe_name')
            description = request.POST.get('recipe_description')
            
            if not name:
                return JsonResponse({'success': False, 'error': 'Recipe name is required'}, status=400)

            user = request.user
            if not user or not user.is_authenticated:
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
                
            return JsonResponse({'success': True, 'recipe_id': recipe.id, 'redirect_url': '/app/profile/'}, status=201)
            
        except Exception as e:
            logger.error(f"Error creating recipe: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return render(request, 'add_recipe.html')

@login_required(login_url='/app/login_alert/')
def food_delete(request, pk):
    if request.method == "POST":
        food = get_object_or_404(Food, pk=pk, user=request.user)
        food.delete()
    return redirect('profile') 

@login_required(login_url='/app/login_alert/')
def recipe_delete(request, pk):
    if request.method == "POST":
        recipe = get_object_or_404(Recipe, pk=pk, user=request.user)
        recipe.delete()
    return redirect('profile')

# Create your views here.
# 簡單聊天室功能
@login_required
def simple_chat(request):
    """簡單聊天室頁面"""
    user = request.user
    
    # 尋找第一個食物來創建聊天室（用於測試）
    food = Food.objects.first()
    if not food:
        return render(request, 'simple_chat.html', {'error': '請先添加一些食物'})
    
    # 尋找已存在的聊天室（不論當前用戶是買方或賣方）
    meetup = Meetup.objects.filter(food=food).first()
    
    if not meetup:
        # 如果沒有聊天室，創建一個新的
        # 獲取所有用戶
        all_users = CustomUser.objects.all()
        if all_users.count() < 2:
            return render(request, 'simple_chat.html', {'error': '需要至少兩個用戶才能聊天'})
        
        # 確定買方和賣方
        if user == food.user:
            # 當前用戶是食物擁有者，作為賣方
            seller = user
            buyer = CustomUser.objects.exclude(id=user.id).first()
        else:
            # 當前用戶不是食物擁有者，作為買方
            buyer = user
            seller = food.user
        
        meetup = Meetup.objects.create(
            food=food,
            buyer=buyer,
            seller=seller
        )
    
    # 獲取聊天紀錄
    messages = meetup.messages.all().order_by('send_time')
    
    return render(request, 'simple_chat.html', {
        'meetup': meetup,
        'messages': messages,
        'current_user': user
    })

@csrf_exempt
@login_required  
def send_message(request):
    """發送訊息"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            meetup_id = data.get('meetup_id')
            content = data.get('content', '').strip()
            
            if not content:
                return JsonResponse({'success': False, 'error': '訊息不能為空'})
                
            meetup = get_object_or_404(Meetup, id=meetup_id)
            
            # 創建訊息
            message = Message.objects.create(
                meetup=meetup,
                sender=request.user,
                content=content
            )
            
            return JsonResponse({
                'success': True,
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'sender': message.sender.username,
                    'sender_avatar': message.sender.avatar.url if message.sender.avatar else None,
                    'send_time': message.send_time.strftime('%H:%M'),
                    'is_mine': message.sender == request.user
                }
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': '方法不允許'})

@login_required
def get_messages(request, meetup_id):
    """獲取聊天紀錄"""
    meetup = get_object_or_404(Meetup, id=meetup_id)
    messages = meetup.messages.all().order_by('send_time')
    
    messages_data = []
    for msg in messages:
        messages_data.append({
            'id': msg.id,
            'content': msg.content,
            'sender': msg.sender.username,
            'sender_avatar': msg.sender.avatar.url if msg.sender.avatar else None,
            'send_time': msg.send_time.strftime('%H:%M'),
            'is_mine': msg.sender == request.user
        })
    
    return JsonResponse({'messages': messages_data})

@login_required
def start_chat(request, food_id):
    """開始與賣家聊天"""
    food = get_object_or_404(Food, id=food_id)
    current_user = request.user
    
    # 檢查是否為食物擁有者
    if current_user == food.user:
        return render(request, 'chat.html', {
            'error': '您不能與自己聊天',
            'meetup': None
        })
    
    # 查找已存在的聊天室
    meetup = Meetup.objects.filter(
        food=food,
        buyer=current_user,
        seller=food.user
    ).first()
    
    # 如果沒有聊天室，創建一個新的
    if not meetup:
        meetup = Meetup.objects.create(
            food=food,
            buyer=current_user,
            seller=food.user
        )
    
    # 獲取聊天紀錄
    messages = meetup.messages.all().order_by('send_time')
    
    return render(request, 'chat.html', {
        'meetup': meetup,
        'messages': messages,
        'current_user': current_user,
        'user': current_user
    })

@login_required
def chat_list(request):
    """聊天室列表"""
    current_user = request.user
    
    # 獲取用戶參與的所有聊天室（作為買方或賣方）
    meetups = Meetup.objects.filter(
        Q(buyer=current_user) | Q(seller=current_user)
    ).select_related('food', 'buyer', 'seller').order_by('-create_time')
    
    # 為每個聊天室添加最後一條訊息和對方用戶信息
    chat_rooms = []
    for meetup in meetups:
        # 獲取最後一條訊息
        last_message = meetup.messages.order_by('-send_time').first()
        
        # 確定對方用戶
        other_user = meetup.seller if current_user == meetup.buyer else meetup.buyer
        
        # 計算未讀訊息數量（簡化版本，這裡假設所有訊息都是已讀）
        unread_count = 0
        
        chat_rooms.append({
            'meetup': meetup,
            'other_user': other_user,
            'last_message': last_message,
            'unread_count': unread_count,
            'is_seller': current_user == meetup.seller
        })
    
    return render(request, 'chat_list.html', {
        'chat_rooms': chat_rooms,
        'current_user': current_user
    })

@login_required
def chat_room(request, meetup_id):
    """直接進入特定聊天室"""
    meetup = get_object_or_404(Meetup, id=meetup_id)
    current_user = request.user
    
    # 檢查用戶是否有權限訪問此聊天室
    if current_user != meetup.buyer and current_user != meetup.seller:
        return render(request, 'chat.html', {
            'error': '您沒有權限訪問此聊天室',
            'meetup': None
        })
    
    # 獲取聊天紀錄
    messages = meetup.messages.all().order_by('send_time')
    
    return render(request, 'chat.html', {
        'meetup': meetup,
        'messages': messages,
        'current_user': current_user,
        'user': current_user
    })

