from rest_framework import permissions, viewsets
# from users.models import User
from django.contrib.auth import get_user_model
from recipes.models import Tag, Ingredient, Recipe
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeSerializer, RecipeGETSerializer,
                          RecipePOSTSerializer, UserSerializer)
from rest_framework.decorators import action
from rest_framework.response import Response

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


# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     lookup_field = 'username'
#
#     def get_permissions(self):
#         if self.action in ['get', 'list']:
#             permission_classes = (permissions.IsAuthenticated,)
#         else:
#             permission_classes = (permissions.AllowAny,)
#         return [permission() for permission in permission_classes]

    # @action(detail=True, methods=['get'])
    # def me(self, request):
    #     return Response({'r': request.user.username})
