from django.shortcuts            import render, get_object_or_404
from django.http                 import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models            import Q
from .models                     import Recipe, RecipeIngredient, Food

# Create your views here.

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

def search_recipe(request):
    if request.method == 'GET':
        search_term = request.GET.get('simple-search', None)

        recipes = Recipe.objects.filter(
            Q(name__icontains=search_term) |
            Q(description__icontains=search_term) |
            Q(recipe_ingredients__ingredient__name__icontains=search_term)
        ).distinct()

        result = []
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
                'user': str(recipe.user),
                'ingredients': ingredients_data
            }
            result.append(recipe_data)

        return JsonResponse(result, safe=False)
    else:
        return HttpResponse(status=405, reason='Method Not Allowed')
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    ingredients = RecipeIngredient.objects.filter(recipe=recipe)
    
    context = {
        'recipe': recipe,
        'ingredients': ingredients,
    }
    
    return render(request, 'recipe_detail.html', context)

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

def map_view(request):
    search_term = request.GET.get('search', '')
    return render(request, 'map.html', {'search_term': search_term})

def api_search(request):
    if request.method == 'GET':
        search_term = request.GET.get('simple-search', '')
        foods = Food.objects.filter(
            Q(name__icontains=search_term) |
            Q(description__icontains=search_term)
        ).filter(is_soldout=False)

        result = []
        for food in foods:
            food_data = {
                'id': food.id,
                'name': food.name,
                'description': food.description,
                'quantity': food.quantity,
                'unit': food.unit,
                'price': str(food.price),
                'expiration': food.expiration_date.strftime('%Y-%m-%d'),
                'user': str(food.user),
                'food_address': food.food_address,
                'latitude': food.latitude,
                'longitude': food.longitude
            }
            result.append(food_data)

        return JsonResponse(result, safe=False)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)
