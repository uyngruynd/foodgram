# Generated by Django 3.2.18 on 2023-02-25 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_auto_20230221_2044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(default=None, max_length=1024, null=True, upload_to='backend_media/', verbose_name='Картинка'),
        ),
    ]
