from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Переопределенная модель пользователя."""
    username = models.CharField(max_length=200, unique=True, )
    email = models.EmailField(max_length=200, unique=True, )
    first_name = models.CharField(max_length=200, )
    last_name = models.CharField(max_length=200, )
    password = models.CharField(max_length=200, )
    shopping_list = models.ManyToManyField('recipes.Recipe',
                                           through='recipes.ShoppingList', )

    REQUIRED_FIELDS = ['first_name', 'last_name', ]


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
