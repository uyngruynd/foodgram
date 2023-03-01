from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Модель для работы с тегами."""
    name = models.CharField(max_length=200, verbose_name='Имя', )
    color = models.CharField(max_length=16, verbose_name='Цвет', )
    slug = models.SlugField(max_length=50, )

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'color', 'slug', ],
                                    name='unique tag', )
        ]
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    """Модель для работы с ингредиентами."""
    name = models.CharField(max_length=200, verbose_name='Имя', )
    measurement_unit = models.CharField(max_length=20,
                                        verbose_name='Единица измерения', )

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='unique ingredient', )
        ]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    """Модель для работы с рецептами."""
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='Автор', )
    name = models.CharField(max_length=200, verbose_name='Имя', )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes_images/',
        max_length=1024,
    )
    text = models.TextField()
    ingredients = models.ManyToManyField(Ingredient,
                                         through='IngredientRecipe',
                                         related_name='recipes',
                                         verbose_name='Ингредиенты', )
    tags = models.ManyToManyField(Tag,
                                  related_name='recipes',
                                  verbose_name='Теги', )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления, мин.', )
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации', )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class IngredientRecipe(models.Model):
    """Модель, связывающая рецепт с ингредиентами."""
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   verbose_name='Ингредиент',
                                   related_name='recipe', )
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт',
                               related_name='ingredient', )
    amount = models.PositiveSmallIntegerField(verbose_name='Количество', )

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['ingredient', 'recipe'],
                                    name='unique ingredient_recipe', )
        ]

    class Meta:
        verbose_name = 'Ингредиенты в рецептах'


class ShoppingList(models.Model):
    """Модель для работы со списком покупок."""
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь',
                             related_name='shopping', )
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт',
                               related_name='shopping', )

    def __str__(self):
        return f'{self.user} - {self.recipe}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique shopping_list', )
        ]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'


class FavoritesList(models.Model):
    """Модель для работы со списком избранного."""
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь',
                             related_name='favorites')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт',
                               related_name='favorites')

    def __str__(self):
        return f'{self.user} - {self.recipe}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique favorites_list', )
        ]
        verbose_name = 'Список избранного'
        verbose_name_plural = 'Списки избранного'
