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
