from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm, CustomUserChangeForm, FoodForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Food
import json

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

