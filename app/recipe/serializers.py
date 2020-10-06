from rest_framework import serializers
from recipe import models


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag objects"""

    class Meta():
        model = models.Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta():
        model = models.Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.PrimaryKeyRelatedField(
        queryset=models.Ingredient.objects.all(),
        many=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=models.Tag.objects.all(),
        many=True,
    )

    class Meta():
        model = models.Recipe
        fields = [
            'id',
            'title',
            'time_minutes',
            'price',
            'ingredients',
            'tags',
            'link'
        ]
        read_only_fields = ['id']

    def validate_time_minutes(self, value):
        """Validate time_minutes field"""
        if value < 0:
            raise serializers.ValidationError(
                "Time duration cannot be negative!")
        return value

    def validate_price(self, value):
        """Validate time_minutes field"""
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative!")
        return value


class RecipeDetailSerializer(RecipeSerializer):
    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipes"""

    class Meta:
        model = models.Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
