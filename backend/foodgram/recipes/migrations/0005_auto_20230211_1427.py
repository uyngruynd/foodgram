# Generated by Django 2.2.16 on 2023-02-11 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_auto_20230210_2207'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(upload_to='static/images/', verbose_name='Картинка'),
        ),
    ]