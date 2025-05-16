from django.shortcuts            import render
from django.http                 import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models            import Q
from .models                     import Food
import logging

logger = logging.getLogger(__name__)

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

