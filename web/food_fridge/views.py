from django.shortcuts import render
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
def send_simple_message(request):
    """發送簡單訊息"""
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
                    'send_time': message.send_time.strftime('%H:%M'),
                    'is_mine': message.sender == request.user
                }
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': '方法不允許'})

@login_required
def get_simple_messages(request, meetup_id):
    """獲取聊天紀錄"""
    meetup = get_object_or_404(Meetup, id=meetup_id)
    messages = meetup.messages.all().order_by('send_time')
    
    messages_data = []
    for msg in messages:
        messages_data.append({
            'id': msg.id,
            'content': msg.content,
            'sender': msg.sender.username,
            'send_time': msg.send_time.strftime('%H:%M'),
            'is_mine': msg.sender == request.user
        })
    
    return JsonResponse({'messages': messages_data})

@login_required
def chat_test(request):
    """聊天室測試頁面"""
    user = request.user
    
    # 尋找第一個食物來創建聊天室（用於測試）
    food = Food.objects.first()
    if not food:
        return render(request, 'chat_test.html', {'error': '請先添加一些食物'})
    
    # 尋找已存在的聊天室（不論當前用戶是買方或賣方）
    try:
        meetup = Meetup.objects.filter(food=food).first()
        
        if not meetup:
            # 如果沒有聊天室，創建一個新的
            all_users = CustomUser.objects.all()
            if all_users.count() < 2:
                return render(request, 'chat_test.html', {'error': '需要至少兩個用戶才能聊天'})
            
            # 確定買方和賣方
            if user == food.user:
                seller = user
                buyer = CustomUser.objects.exclude(id=user.id).first()
            else:
                buyer = user
                seller = food.user
            
            meetup = Meetup.objects.create(
                food=food,
                buyer=buyer,
                seller=seller
            )
            
    except Exception as e:
        return render(request, 'chat_test.html', {'error': f'創建聊天室失敗: {str(e)}'})
    
    return render(request, 'chat_test.html', {
        'meetup': meetup,
        'current_user': user
    })