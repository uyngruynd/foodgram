# from users.models import User
from django.contrib.auth import get_user_model
from recipes.models import Ingredient, Recipe, Tag
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import Follow

from .serializers import (CustomUserSerializer, CustomUserCreateSerializer,
                          IngredientSerializer, RecipeGETSerializer,
                          RecipePOSTSerializer, RecipeSerializer,
                          TagSerializer)

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return RecipePOSTSerializer
        return RecipeGETSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_permissions(self):
        if self.action in ['get', 'list']:
            permission_classes = (permissions.AllowAny,)
        else:
            permission_classes = (permissions.IsAuthenticated,)
        return [permission() for permission in permission_classes]


class UserViewSet(viewsets.ModelViewSet):
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
        # FIXME - тут нужно написать запрос через select_related
        # authors = Follow.objects.filter(user=self.request.user).select_related('author')
        follows = Follow.objects.filter(user=self.request.user)
        authors = []
        for follow in follows:
            authors.append(follow.author)

        page = self.paginate_queryset(authors)
        serializer = self.get_serializer(page, many=True)

        data = serializer.data

        for author in data:
            recipes = Recipe.objects.filter(
                author__id=author.get('id')).values('id', 'name', 'image',
                                                    'cooking_time')
            author['recipes'] = recipes
        return self.get_paginated_response(data)

    @action(methods=['post', 'delete'], detail=False,
            url_path=r'(?P<pk>\d+)/subscribe', )
    def subscribe(self, request, pk):
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
            recipes = Recipe.objects.filter(
                author__id=pk).values('id', 'name', 'image',
                                      'cooking_time')
            data = serializer.data
            data['recipes'] = recipes
            return Response(data)
        else:
            if not follow.exists():
                return Response('Вы не подписаны на этого автора!',
                                status=status.HTTP_400_BAD_REQUEST, )
            follow.delete()
            return Response({'errors': ''})

    @action(detail=False, url_path='me')
    def me(self, request):
        me = self.request.user
        serializer = self.get_serializer(me)
        return Response(serializer.data)
