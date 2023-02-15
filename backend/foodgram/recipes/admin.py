from django.contrib import admin

from .models import Ingredient, Recipe, Tag

# class TagInline(admin.TabularInline):
#     model = Tag
#
#
# class IngredientInline(admin.TabularInline):
#     model = Ingredient


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройки отображения модели Recipe в интерфейсе админки."""
    list_display = ('name', 'author',)
    list_filter = ('name', 'author', 'tags',)
    empty_value_display = '-пусто-'
    # inlines = [TagInline, IngredientInline, ]

    # TODO: На странице рецепта вывести общее число добавлений этого рецепта в избранное


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройки отображения модели Ingredient в интерфейсе админки."""
    list_display = ('name', 'measurement_unit',)
    empty_value_display = '-пусто-'


admin.site.register(Tag)
