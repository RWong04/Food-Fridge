from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm  
from .models import CustomUser, Food

class CustomUserCreationForm(UserCreationForm):
    avatar = forms.ImageField(required=False)
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'avatar', 'password1', 'password2')
        
class CustomUserChangeForm(UserChangeForm):
    avatar = forms.ImageField(required=False)
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'avatar')

class LoginForm(AuthenticationForm):
    # 可自訂欄位（例如加上 Bootstrap 樣式）
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


class FoodForm(forms.ModelForm):
    class Meta:
        model = Food
        fields = [
            'name', 'category', 'description', 'quantity', 'unit',
            'price', 'expiration_date', 'img_path', 'latitude', 'longitude', 'is_soldout'
        ]
