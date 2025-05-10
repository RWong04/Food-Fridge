from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# 自訂用戶模型，擴充頭像欄位
class CustomUser(AbstractUser):
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name="customuser_groups",  # 關鍵設定
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name="customuser_permissions",  # 關鍵設定
        related_query_name="customuser",
    )

    def __str__(self):
        return self.username

# 食物分類選項
class FoodCategory(models.IntegerChoices):
    INGREDIENT = 0, '食材'
    COOKED = 1, '熟食'
    OTHER = 2, '其他'

# 食物模型
class Food(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='foods')
    name = models.CharField(max_length=32)
    category = models.IntegerField(choices=FoodCategory.choices)
    description = models.TextField(blank=True)
    quantity = models.FloatField(help_text="數量，例如 0.5 代表半條")
    unit = models.CharField(max_length=16, default='條', help_text="單位，如條、片、份")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    expiration_date = models.DateField()
    create_time = models.DateTimeField(auto_now_add=True)
    img_path = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    food_address = models.CharField(max_length=255, blank=True)  # 新增地址欄位
    is_soldout = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}（{self.quantity}{self.unit}）"

# 聊天室
class Meetup(models.Model):
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name='meetups')
    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='buy_meetups')
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sell_meetups')
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.food.name} 的聊天室"

# 聊天訊息
class Message(models.Model):
    meetup = models.ForeignKey(Meetup, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    send_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:20]}"

# 交易記錄
class FoodTransaction(models.Model):
    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='purchases')
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sales')
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name='transactions')
    quantity = models.FloatField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    transaction_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"交易：{self.food.name} x {self.quantity}"

# 食譜
class Recipe(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='recipes')
    name = models.CharField(max_length=32)
    description = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# 食材
class Ingredient(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name

# 食譜-食材關聯
class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='ingredient_recipes')
    quantity = models.FloatField()
    unit = models.CharField(max_length=16)

    class Meta:
        unique_together = ('recipe', 'ingredient')

    def __str__(self):
        return f"{self.recipe.name} 需要 {self.quantity}{self.unit} {self.ingredient.name}"