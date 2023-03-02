from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import (BooleanFilter, DjangoFilterBackend,
                                           FilterSet,
                                           ModelMultipleChoiceFilter)
from djoser.views import UserViewSet
from recipes.models import (FavoritesList, Ingredient, IngredientRecipe,
                            Recipe, ShoppingList, Tag)
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import Follow, User

from .permissions import IsAuthorOrReadOnly
from .serializers import (CustomUserCreateSerializer, CustomUserSerializer,
                          IngredientSerializer, PasswordSerializer,
                          RecipeBaseSerializer, RecipeGETSerializer,
                          RecipePOSTSerializer, RecipeSerializer,
                          TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с моделью Tag."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с моделью Ingredient."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class RecipeFilter(FilterSet):
    """Кастомный фильтр для фильтрации во вьюсете рецепта."""
    tags = ModelMultipleChoiceFilter(field_name='tags__slug',
                                     to_field_name='slug',
                                     queryset=Tag.objects.all(), )

    is_favorited = BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = BooleanFilter(method='filter_is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return queryset
        return queryset.filter(favorites__user=user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return queryset
        return queryset.filter(shopping__user=user)

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart', ]


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с моделью Recipe."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated,
                                  IsAuthorOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return RecipePOSTSerializer
        return RecipeGETSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['get'], detail=False,
            url_path='download_shopping_cart', )
    def get_download_shopping_cart(self, request):
        """Функция предназначена для выгрузки в файл списка покупок."""
        recipes_list = list(ShoppingList.objects.filter(
            user=self.request.user).values_list('recipe', flat=True))
        ingredients = IngredientRecipe.objects.filter(
            recipe_id__in=
            recipes_list).values('ingredient__name',
                                 'ingredient__measurement_unit').annotate(
            total_amount=Sum('amount'))

        response = HttpResponse(content_type='text/plain')
        response[
            'Content-Disposition'] = (
            'attachment; filename="my_shopping_cart.txt"')

        response.write('Мой список покупок:\n')
        for row_num, ingredient in enumerate(ingredients, start=1):
            response.write(
                f'{row_num}: {ingredient.get("ingredient__name")} - '
                f'{ingredient.get("total_amount")} '
                f'{ingredient.get("ingredient__measurement_unit")}\n')

        return response

    @action(methods=['post', 'delete'], detail=True,
            url_path='shopping_cart', )
    def get_shopping_cart(self, request, pk):
        """Функция для работы с корзиной."""
        return self.__add_delete_recipe_relation(request, pk, ShoppingList,
                                                 'корзине!')

    @action(methods=['post', 'delete'], detail=True,
            url_path='favorite', )
    def get_favorite(self, request, pk):
        """Функция для работы с избранным."""
        return self.__add_delete_recipe_relation(request, pk, FavoritesList,
                                                 'избранном!')

    def __add_delete_recipe_relation(self, request, pk, model, table_name):
        recipe = Recipe.objects.get(pk=pk)

        obj = model.objects.filter(recipe=recipe, user=self.request.user)
        serializer = self.get_serializer(recipe)

        if request.method == "POST":
            if obj.exists():
                return Response(f'Этот рецепт уже в {table_name}',
                                status=status.HTTP_400_BAD_REQUEST, )
            new_obj = model(recipe=recipe, user=self.request.user)
            new_obj.save()
            return Response(serializer.data)
        else:
            if not obj.exists():
                return Response(f'Этого рецепта нет в {table_name}',
                                status=status.HTTP_400_BAD_REQUEST, )
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class CustomUserViewSet(UserViewSet):
    """Вьюсет для работы с моделью User."""
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['POST', 'DELETE']:
            return CustomUserCreateSerializer
        return CustomUserSerializer

    def get_permissions(self):
        if self.action in ['get', 'list']:
            permission_classes = (permissions.IsAuthenticated,)
        else:
            permission_classes = (permissions.AllowAny,)
        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=False, url_path='subscriptions', )
    def subscriptions(self, request):
        """Функция возвращает список подписок."""
        authors = User.objects.filter(following__user=self.request.user)
        page = self.paginate_queryset(authors)
        serializer = self.get_serializer(page, many=True)

        data = serializer.data

        for author in data:
            recipes = Recipe.objects.filter(author__id=author.get('id'))
            recipes_serializer = RecipeBaseSerializer(recipes, many=True,
                                                      read_only=True)
            author['recipes'] = recipes_serializer.data
        return self.get_paginated_response(data)

    @action(methods=['post', 'delete'], detail=False,
            url_path=r'(?P<pk>\d+)/subscribe', )
    def subscribe(self, request, pk):
        """Функция для работы с подписками."""
        author = User.objects.get(pk=pk)

        if author == self.request.user:
            return Response('Нельзя подписаться на самого себя!',
                            status=status.HTTP_400_BAD_REQUEST, )
        follow = Follow.objects.filter(user=self.request.user, author=author)

        if request.method == "POST":
            if follow.exists():
                return Response('Вы уже подписаны на этого автора!',
                                status=status.HTTP_400_BAD_REQUEST, )

            new_follow = Follow(author=author, user=self.request.user)
            new_follow.save()

            serializer = self.get_serializer(author)

            recipes = Recipe.objects.filter(author__id=pk)
            recipes_serializer = RecipeBaseSerializer(recipes, many=True,
                                                      read_only=True)
            data = serializer.data
            data['recipes'] = recipes_serializer.data
            return Response(data)
        else:
            if not follow.exists():
                return Response('Вы не подписаны на этого автора!',
                                status=status.HTTP_400_BAD_REQUEST, )
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, url_path='me')
    def me(self, request):
        """Функция возвращает данные профиля текущего пользователя."""
        me = self.request.user
        serializer = self.get_serializer(me)
        return Response(serializer.data)

    @action(["post"], detail=False, url_path='set_password')
    def set_password(self, request):
        """Функция меняет пароль пользователя."""
        serializer = PasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not self.request.user.check_password(
                serializer.data.get("current_password")):
            return Response({"current_password": ["Wrong password."]},
                            status=status.HTTP_400_BAD_REQUEST)
        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
