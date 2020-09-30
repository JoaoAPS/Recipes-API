from django.test import TestCase
from django.contrib.auth import get_user_model
from django.shortcuts import reverse

from rest_framework.test import APIClient
from rest_framework import status

from recipe.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPE_LIST_URL = reverse('recipe:recipe-list')


def recipe_detail_url(id):
    return reverse('recipe:recipe-detail', args=[id])


def sample_user(email='sample@gotmail.com', password='ajsd', name='Sample'):
    return get_user_model().objects.create_user(
        email=email, password=password, name=name
    )


def sample_recipe(user, **params):
    defaults = {
        'title': 'Test Recipe',
        'time_minutes': 5,
        'price': 50.0
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


def sample_ingredient(user, name='Test Ing'):
    return Ingredient.objects.create(user=user, name=name)


def sample_tag(user, name='Test Tag'):
    return Tag.objects.create(user=user, name=name)


class PublicRecipeApiTests(TestCase):
    """Tests for public requests on Recipe API"""

    def setUp(self):
        self.client = APIClient()

    def test_unauthorized_retrieve_invalid(self):
        """Test that recipes cannot be retrieved by an unauthorized user"""
        res = self.client.get(RECIPE_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Tests for private requests on Recipe API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@gotmail.com',
            password='testpass',
            name='Test User'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_list_successful(self):
        """Test that an authenticated user can retrieve the recipes"""
        sample_recipe(self.user)
        recipe = sample_recipe(
            self.user,
            title='Test Recipe 2',
            time_minutes=10,
            price=15.00
        )
        recipe.ingredients.add(sample_ingredient(self.user))
        recipe.tags.add(sample_tag(self.user))

        serializer = RecipeSerializer(
            Recipe.objects.all().order_by('title'),
            many=True
        )
        res = self.client.get(RECIPE_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_authenticated_user(self):
        """Test that the authenticated user get their recipes only"""
        recipe = sample_recipe(self.user)
        sample_recipe(
            user=sample_user(),
            title='Other Recipe',
            time_minutes=7,
            price=10.1
        )

        serializer = RecipeSerializer(recipe)
        res = self.client.get(RECIPE_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0], serializer.data)

    def test_retrieve_recipe_detail(self):
        """Test retrieving the recipe details"""
        recipe = sample_recipe(self.user)
        recipe.ingredients.add(sample_ingredient(self.user))
        recipe.tags.add(sample_tag(self.user))

        serializer = RecipeDetailSerializer(recipe)
        res = self.client.get(recipe_detail_url(recipe.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_other_user_recipe_forbidden(self):
        """Test a user cannot retrive a recipe from another user"""
        recipe = sample_recipe(sample_user())
        res = self.client.get(recipe_detail_url(recipe.id))

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
