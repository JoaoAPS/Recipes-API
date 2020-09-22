# Generated by Django 2.1.15 on 2020-09-22 23:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0003_recipe'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='name',
            new_name='title',
        ),
        migrations.AddField(
            model_name='recipe',
            name='link',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='recipe',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recipe',
            name='time_minutes',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
