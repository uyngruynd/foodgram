from django.contrib import admin

from .models import FavoritesList, Ingredient, Recipe, Tag


class TagInline(admin.TabularInline):
    model = Recipe.tags.through


class IngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройки отображения модели Recipe в интерфейсе админки."""
    list_display = ('name', 'author', 'is_favourite_count', )
    list_filter = ('name', 'author', 'tags', )
    empty_value_display = '-пусто-'

    inlines = [TagInline, IngredientInline, ]

    def is_favourite_count(self, obj):
        return FavoritesList.objects.filter(recipe=obj).count()

    is_favourite_count.short_description = (
        'Встречается в избранном')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройки отображения модели Ingredient в интерфейсе админки."""
    list_display = ('name', 'measurement_unit',)
    empty_value_display = '-пусто-'


admin.site.register(Tag)
