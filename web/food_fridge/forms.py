from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm  
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')  # 加入你想在註冊表單顯示的欄位
        
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')  # 可用於後續修改資料

class LoginForm(AuthenticationForm):
    # 可自訂欄位（例如加上 Bootstrap 樣式）
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
