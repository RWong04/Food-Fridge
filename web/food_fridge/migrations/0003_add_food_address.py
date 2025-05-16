# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("food_fridge", "0002_alter_food_img_path"),
    ]

    operations = [
        migrations.AddField(
            model_name="food",
            name="food_address",
            field=models.CharField(blank=True, max_length=255, default=''),
            preserve_default=False,
        ),
    ]
