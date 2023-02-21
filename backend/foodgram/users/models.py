from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Переопределенная модель пользователя."""
    username = models.CharField(max_length=200,
                                unique=True,
                                verbose_name='Имя пользователя', )
    email = models.EmailField(max_length=200,
                              unique=True,
                              verbose_name='Адрес электронной почты', )
    first_name = models.CharField(max_length=200, verbose_name='Имя', )
    last_name = models.CharField(max_length=200, verbose_name='Фамилия', )
    password = models.CharField(max_length=200, verbose_name='Пароль', )
    shopping_list = models.ManyToManyField('recipes.Recipe',
                                           through='recipes.ShoppingList',
                                           verbose_name='Список покупок', )

    REQUIRED_FIELDS = ['first_name', 'last_name', ]


class Follow(models.Model):
    """Модель для работы с подписками."""
    user = models.ForeignKey('users.User',
                             on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Пользователь', )
    author = models.ForeignKey('users.User',
                               on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='Автор', )

    def __str__(self):
        return f'{self.user} - {self.author}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique follow', )
        ]
