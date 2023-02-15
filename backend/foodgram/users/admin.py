from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Настройки отображения модели User в интерфейсе админки."""
    list_filter = ('username', 'email', )
    empty_value_display = '-пусто-'
