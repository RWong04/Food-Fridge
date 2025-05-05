from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from .forms import LoginForm
import json

@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # 根據你的 CustomUserCreationForm 欄位調整
            form = CustomUserCreationForm(data)
        except Exception:
            return JsonResponse({
                "message": "Invalid JSON.",
                "error_code": 103
            }, status=400)
        if form.is_valid():
            user = form.save()
            return JsonResponse(
                {"message": "Register successfully!"},
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
            return JsonResponse({"message": "Login successfully!"}, status=201)
        else:
            return JsonResponse({
                "message": "帳號或密碼錯誤！",
                "error_code": 101
            }, status=400)
    return render(request, "login.html")