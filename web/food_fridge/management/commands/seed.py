from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from food_fridge.models import Food, Recipe, Ingredient, RecipeIngredient
from django.utils import timezone
from datetime import timedelta
from django_seed import Seed

class Command(BaseCommand):
    seeder = Seed.seeder()
    help = 'Seed database with sample data'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        # 建立用戶
        user, _ = User.objects.get_or_create(username='小明', defaults={
            'email': 'xiaoming@gmail.com'
        })
        user.set_password('123')
        user.save()
        
        mei, _ = User.objects.get_or_create(username='小美', defaults={
            'email': 'xiaomei@gmail.com'
        })
        mei.set_password('123')
        mei.save()

        # 建立食材
        apple, _ = Ingredient.objects.get_or_create(name='蘋果')
        flour, _ = Ingredient.objects.get_or_create(name='麵粉')
        butter, _ = Ingredient.objects.get_or_create(name='奶油')

        # 建立剩食
        food1, _ = Food.objects.get_or_create(
            user=user,
            name='蘋果',
            category=0,
            description='新鮮多汁的蘋果，但我吃不完',
            quantity=5,
            unit='顆',
            price=30,
            expiration_date=timezone.now().date() + timedelta(days=7),
            latitude=22.9864,
            longitude=120.2194,
            food_address='台南市東區大學路1號'
        )
        food2, _ = Food.objects.get_or_create(
            user=mei,
            name='香蕉',
            category=0,
            description='熟透的香蕉，適合做香蕉蛋糕。',
            quantity=8,
            unit='根',
            price=40,
            expiration_date=timezone.now().date() + timedelta(days=3),
            latitude=22.9836,
            longitude=120.2250,
            food_address='台南市東區勝利路85號'
        )
        food3, _ = Food.objects.get_or_create(
            user=user,
            name='牛奶',
            category=1,
            description='全脂牛奶，未開封。',
            quantity=2,
            unit='瓶',
            price=60,
            expiration_date=timezone.now().date() + timedelta(days=5),
            latitude=22.9912,
            longitude=120.2177,
            food_address='台南市東區東寧路300號'
        )
        food4, _ = Food.objects.get_or_create(
            user=mei,
            name='雞蛋',
            category=1,
            description='放山雞蛋，新鮮健康。',
            quantity=12,
            unit='顆',
            price=55,
            expiration_date=timezone.now().date() + timedelta(days=10),
            latitude=22.9805,
            longitude=120.2268,
            food_address='台南市東區崇德路100號'
        )
        food5, _ = Food.objects.get_or_create(
            user=user,
            name='麵包',
            category=2,
            description='放了兩天的法國麵包，最好盡快吃完。',
            quantity=3,
            unit='條',
            price=90,
            expiration_date=timezone.now().date() + timedelta(days=2),
            latitude=22.9840,
            longitude=120.2215,
            food_address='台南市東區林森路二段200號'
        )
        food6, _ = Food.objects.get_or_create(
            user=mei,
            name='高麗菜',
            category=0,
            description='高山高麗菜，吃起來很清甜。',
            quantity=0.5,
            unit='顆',
            price=35,
            expiration_date=timezone.now().date() + timedelta(days=6),
            latitude=22.9888,
            longitude=120.2233,
            food_address='台南市東區裕農路500號'
        )
        food7, _ = Food.objects.get_or_create(
            user=user,
            name='馬鈴薯',
            category=0,
            description='台灣本地馬鈴薯，適合燉煮。',
            quantity=10,
            unit='顆',
            price=50,
            expiration_date=timezone.now().date() + timedelta(days=8),
            latitude=22.9901,
            longitude=120.2202,
            food_address='台南市東區東門路二段300號'
        )
        food8, _ = Food.objects.get_or_create(
            user=mei,
            name='胡蘿蔔',
            category=0,
            description='有機胡蘿蔔，甜脆可口。',
            quantity=6,
            unit='條',
            price=28,
            expiration_date=timezone.now().date() + timedelta(days=9),
            latitude=22.9875,
            longitude=120.2188,
            food_address='台南市東區長榮路一段150號'
        )
        food9, _ = Food.objects.get_or_create(
            user=user,
            name='鮮奶油',
            category=1,
            description='動物性鮮奶油，未開封。',
            quantity=1,
            unit='瓶',
            price=80,
            expiration_date=timezone.now().date() + timedelta(days=4),
            latitude=22.9852,
            longitude=120.2244,
            food_address='台南市東區中華東路三段88號'
        )
        food10, _ = Food.objects.get_or_create(
            user=mei,
            name='番茄',
            category=0,
            description='新鮮番茄，適合做沙拉。',
            quantity=7,
            unit='顆',
            price=32,
            expiration_date=timezone.now().date() + timedelta(days=5),
            latitude=22.9899,
            longitude=120.2166,
            food_address='台南市東區裕信路60號'
        )

        # 建立食譜
        recipe, _ = Recipe.objects.get_or_create(
            user=user,
            name='蘋果派',
            description='簡單又美味的蘋果派，適合下午茶。'
        )

        # 建立食譜-食材關聯
        RecipeIngredient.objects.get_or_create(recipe=recipe, ingredient=apple, quantity=2, unit='顆')
        RecipeIngredient.objects.get_or_create(recipe=recipe, ingredient=flour, quantity=200, unit='克')
        RecipeIngredient.objects.get_or_create(recipe=recipe, ingredient=butter, quantity=50, unit='克')

        self.stdout.write(self.style.SUCCESS('Seeding completed!'))