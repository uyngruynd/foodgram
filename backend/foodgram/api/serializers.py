import base64
from abc import ABC

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (FavoritesList, Ingredient, IngredientRecipe,
                            Recipe, ShoppingList, Tag)
from rest_framework import serializers
from users.models import Follow, User


class CustomUserCreateSerializer(UserCreateSerializer):
    """Описание сериализатора для модели User, запись."""

    class Meta:
        model = User
        fields = (
            'id', 'username', 'password', 'email', 'first_name', 'last_name',)


class CustomUserSerializer(UserSerializer):
    """Описание сериализатора для модели User, чтение."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_subscribed',)

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=self.context['request'].user,
                                     author=obj).exists()


class PasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(max_length=255, )
    new_password = serializers.CharField(max_length=255, )

    def validate(self, value):
        if value.get('current_password') == value.get('new_password'):
            raise serializers.ValidationError(
                'Новый пароль должен отличаться от старого!')
        return value


class TagSerializer(serializers.ModelSerializer):
    """Описание сериализатора для модели Tag"""

    class Meta:
        model = Tag

        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """Описание сериализатора для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class RecipeBaseSerializer(serializers.ModelSerializer):
    """Описание упрощенного сериализатора для модели Recipe."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    """Описание сериализатора для модели Recipe."""
    author = UserSerializer(read_only=True, )
    ingredients = IngredientSerializer(many=True, )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',)

    def to_representation(self, instance):
        output = super().to_representation(instance)
        ingredients = output['ingredients']
        for ingredient in ingredients:
            amount = IngredientRecipe.objects.get(
                ingredient=ingredient.get('id'), recipe=instance).amount
            ingredient['amount'] = amount
        return output

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return FavoritesList.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return ShoppingList.objects.filter(user=user, recipe=obj).exists()


class RecipeGETSerializer(RecipeSerializer):
    """Описание сериализатора для модели Recipe, чтение."""
    tags = TagSerializer(many=True, )


class RecipePOSTSerializer(RecipeSerializer):
    """Описание сериализатора для модели Recipe, запись."""
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())

    def validate(self, value):
        cooking_time = value.get('cooking_time')
        try:
            cooking_time = int(cooking_time)
        except ValueError:
            raise serializers.ValidationError(f'Время приготовления '
                                              f'должно быть числом!')
        if cooking_time <= 0 or cooking_time > 5000:
            raise serializers.ValidationError(
                'Время приготовления задано неверно!')
        for ingredient in value.get('ingredients'):
            amount = ingredient.get('amount')
            try:
                amount = int(amount)
            except ValueError:
                raise serializers.ValidationError(f'Количество для '
                                                  f'ингредиента '
                                                  f'{ingredient.get("name")} '
                                                  f'должно быть числом!')
            if amount < 0:
                raise serializers.ValidationError(
                    f'Неверно задано количество для '
                    f'ингредиента: {ingredient.get("name")}!')
        return value

    def to_representation(self, instance):
        output = super().to_representation(instance)
        tags = output['tags']
        new_tags = []
        for tag_id in tags:
            new_tags.append(Tag.objects.values().get(id=tag_id))
        output['tags'] = new_tags
        return output

    def to_internal_value(self, data):
        ingredients = data.get('ingredients')
        for ingredient in ingredients:
            ingredient['name'] = (
                Ingredient.objects.values().get(id=ingredient['id'])['name'])

        image = data.get('image')
        if isinstance(image, str) and image.startswith('data:image'):
            img_format, img_str = image.split(';base64,')
            ext = img_format.split('/')[-1]
            data['image'] = ContentFile(base64.b64decode(img_str),
                                        name='temp.' + ext)
        return data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        for ingredient in ingredients:
            current_ingredient = Ingredient.objects.get(
                id=ingredient.get('id'))
            IngredientRecipe.objects.create(ingredient=current_ingredient,
                                            recipe=recipe,
                                            amount=ingredient.get(
                                                'amount'))
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        for key, value in validated_data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        if tags:
            instance.tags.set(tags)
        if ingredients:
            instance.ingredients.clear()
            for ingredient in ingredients:
                IngredientRecipe.objects.get_or_create(
                    ingredient_id=ingredient.get('id'), recipe=instance,
                    amount=ingredient.get('amount'))
        instance.save()
        return instance
