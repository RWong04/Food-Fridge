from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Food, Meetup, Message, FoodTransaction, Recipe, Ingredient, RecipeIngredient

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('',)}),  # Add any additional fields here
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('',)}),  # Add any additional fields here
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')  # Customize display

@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'quantity', 'unit', 'price', 'expiration_date', 'user', 'is_soldout')
    list_filter = ('category', 'expiration_date', 'is_soldout')
    search_fields = ('name', 'description', 'food_address')
    date_hierarchy = 'create_time'
    #raw_id_fields = ('user',)  # Use raw_id_fields for ForeignKey

@admin.register(Meetup)
class MeetupAdmin(admin.ModelAdmin):
    list_display = ('food', 'buyer', 'seller', 'create_time')
    list_filter = ('create_time',)
    #raw_id_fields = ('food', 'buyer', 'seller')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('meetup', 'sender', 'send_time')
    list_filter = ('send_time',)
    search_fields = ('content',)
    #raw_id_fields = ('meetup', 'sender')

@admin.register(FoodTransaction)
class FoodTransactionAdmin(admin.ModelAdmin):
    list_display = ('food', 'buyer', 'seller', 'quantity', 'price', 'transaction_time')
    list_filter = ('transaction_time',)
    #raw_id_fields = ('buyer', 'seller', 'food')

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'create_time')
    list_filter = ('create_time',)
    search_fields = ('name', 'description')
    #raw_id_fields = ('user',)

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'quantity', 'unit')
    #raw_id_fields = ('recipe', 'ingredient')
    list_filter = ('recipe',)
    
