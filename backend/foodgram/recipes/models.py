from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):
    """Модель для работы с тегами."""
    name = models.CharField(max_length=200, unique=True, )
    color = models.CharField(max_length=16, unique=True, )
    slug = models.SlugField(max_length=50, unique=True, )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель для работы с ингредиентами."""
    name = models.CharField(max_length=200, unique=True, )
    measurement_unit = models.CharField(max_length=20, )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель для работы с рецептами."""
    author = models.ForeignKey(User, on_delete=models.CASCADE, )
    name = models.CharField(max_length=200, )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/',
    )
    text = models.TextField()
    ingredients = models.ManyToManyField(Ingredient,
                                         through='IngredientRecipe', )
    tags = models.ManyToManyField(Tag)
    cooking_time = models.PositiveSmallIntegerField()
    pub_date = models.DateTimeField(auto_now_add=True, )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("-pub_date",)


class IngredientRecipe(models.Model):
    """Модель, связывающая рецепт с ингредиентами."""
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE, )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, )
    amount = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class ShoppingList(models.Model):
    """Модель для работы со списком покупок."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, )

    def __str__(self):
        return f'{self.user} - {self.recipe}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique shopping_list', )
        ]


class FavoritesList(models.Model):
    """Модель для работы со списком избранного."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, )

    def __str__(self):
        return f'{self.user} - {self.recipe}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique favorites_list', )
        ]
