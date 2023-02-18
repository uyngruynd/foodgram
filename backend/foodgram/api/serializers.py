import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag
from rest_framework import serializers
from users.models import Follow

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'username', 'password', 'email', 'first_name', 'last_name',)


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_subscribed',)

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(user=self.context['request'].user,
                                     author=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag

        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            img_format, img_str = data.split(';base64,')
            ext = img_format.split('/')[-1]
            data = ContentFile(base64.b64decode(img_str), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
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
        return True  # FIXME

    def get_is_in_shopping_cart(self, obj):
        return True  # FIXME


class RecipeGETSerializer(RecipeSerializer):
    tags = TagSerializer(many=True, )


class RecipePOSTSerializer(RecipeSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())

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
        instance.tags.set(validated_data.get('tags', instance.tags))
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        ingredients = validated_data.pop('ingredients')
        IngredientRecipe.objects.filter(recipe=instance).delete()
        for ingredient in ingredients:
            IngredientRecipe.objects.get_or_create(
                ingredient_id=ingredient.get('id'), recipe=instance,
                amount=ingredient.get('amount'))
        instance.save()

        return instance
