# Generated by Django 2.1.15 on 2020-10-05 23:08

from django.db import migrations, models
import recipe.models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0004_auto_20200922_2331'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='image',
            field=models.ImageField(null=True, upload_to=recipe.models.recipe_image_file_path),
        ),
    ]