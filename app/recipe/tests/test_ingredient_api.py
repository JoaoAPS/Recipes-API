from django.test import TestCase
from django.contrib.auth import get_user_model
from django.shortcuts import reverse

from rest_framework.test import APIClient
from rest_framework import status

from recipe.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENT_LIST_URL = reverse('recipe:ingredient-list')


class PublicIngredientApiTests(TestCase):
    """Test the ingredient API for public requests"""

    def setUp(self):
        self.client = APIClient()

    def test_ingredient_list_unauthorized(self):
        """Test that authorization is required for retrieving ingredients"""
        res = self.client.get(INGREDIENT_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """Test the ingredient API for private requests"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@gotmail.com",
            password="testpass",
            name="Test Name"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test that an authorized user can retrieve theri ingredients"""
        Ingredient.objects.create(name="Test Ing1", user=self.user)
        Ingredient.objects.create(name="Test Ing2", user=self.user)
        serializer = IngredientSerializer(
            Ingredient.objects.all().order_by('name'),
            many=True
        )
        res = self.client.get(INGREDIENT_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_authenticated_user_ingredients_only(self):
        """Test that only the authenticated user ingredients are retrieved"""
        user2 = get_user_model().objects.create_user(
            email="other@gotmail.com",
            password="ohterpass",
            name="Name 2"
        )
        ing = Ingredient.objects.create(name="Test Ing1", user=self.user)
        Ingredient.objects.create(name="Test Ing2", user=user2)
        res = self.client.get(INGREDIENT_LIST_URL)

        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ing.name)
