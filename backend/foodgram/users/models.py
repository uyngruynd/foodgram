from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Переопределенная модель пользователя."""
    shopping_list = models.ManyToManyField('recipes.Recipe',
                                           through='recipes.ShoppingList', )


class Follow(models.Model):
    """Модель для работы с подписками."""
    user = models.ForeignKey('users.User', on_delete=models.CASCADE,
                             related_name='follower', )
    author = models.ForeignKey('users.User', on_delete=models.CASCADE,
                               related_name='following', )

    def __str__(self):
        return f'{self.user} - {self.author}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique follow', )
        ]
