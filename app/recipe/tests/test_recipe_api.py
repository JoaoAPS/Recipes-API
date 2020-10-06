import tempfile
import os

from PIL import Image

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.shortcuts import reverse

from rest_framework.test import APIClient
from rest_framework import status

from recipe.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPE_LIST_URL = reverse('recipe:recipe-list')


# Helper functions

def recipe_detail_url(id):
    return reverse('recipe:recipe-detail', args=[id])


def image_upload_url(id):
    return reverse('recipe:recipe-upload-image', args=[id])


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


def sample_recipe_payload(**params):
    defaults = {
        'title': 'Test Recipe',
        'time_minutes': 5,
        'price': 50.0
    }
    defaults.update(params)

    return defaults


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

    def test_create_basic_recipe_successful(self):
        """Test creating a new recipe with no ingredients or tags assigned"""
        payload = sample_recipe_payload(link='www.testlink.com')
        res = self.client.post(RECIPE_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Recipe.objects.filter(user=self.user, **payload).exists()
        )

        # Test creating with no link
        payload = sample_recipe_payload()
        res = self.client.post(RECIPE_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(Recipe.objects.all()), 2)
        self.assertTrue(
            Recipe.objects.filter(user=self.user, **payload).exists()
        )

    def test_create_basic_recipe_invalid_payload(self):
        """Test refusing recipe creation with invalid payload"""
        payloads = [
            sample_recipe_payload(title=''),
            sample_recipe_payload(time_minutes=-1),
            sample_recipe_payload(time_minutes=5.4),
            sample_recipe_payload(price=-1.0),
            {
                'time_minutes': 5,
                'price': 50.0
            },
            {
                'title': 'Test',
                'price': 50.0
            },
            {
                'title': 'Test',
                'time_minutes': 5,
            },
        ]

        for payload in payloads:
            res = self.client.post(RECIPE_LIST_URL, payload)

            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(len(Recipe.objects.all()), 0)

    def test_create_full_recipe_successful(self):
        """Test creating a new recipe with ingredients and tags assigned"""
        ingredient1 = sample_ingredient(self.user)
        ingredient2 = sample_ingredient(self.user)
        tag = sample_tag(self.user)

        payload = sample_recipe_payload()
        payload.update({
            'ingredients': [ingredient1.id, ingredient2.id],
            'tags': [tag.id]
        })

        res = self.client.post(RECIPE_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        self.assertEqual(recipe.ingredients.all().count(), 2)
        self.assertEqual(recipe.tags.all().count(), 1)
        self.assertIn(tag, recipe.tags.all())
        self.assertIn(ingredient1, recipe.ingredients.all())
        self.assertIn(ingredient2, recipe.ingredients.all())

    def test_create_full_recipe_invalid_payload(self):
        """Test refusing full recipe creation with invalid payload"""
        payloads = [
            sample_recipe_payload().update({'ingredients': [1000]}),
            sample_recipe_payload().update({'tags': [1000]})
        ]

        for payload in payloads:
            res = self.client.post(RECIPE_LIST_URL, payload)

            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(len(Recipe.objects.all()), 0)

    def test_update_recipe(self):
        """Test updating a recipe"""
        # PUT
        recipe = sample_recipe(user=self.user, price=10.00, time_minutes=10)
        payload = sample_recipe_payload(price=50.00)
        res = self.client.put(recipe_detail_url(recipe.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Recipe.objects.get(id=recipe.id).price,
            payload['price']
        )

        # PATCH
        payload = {'time_minutes': 30}
        res = self.client.patch(recipe_detail_url(recipe.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Recipe.objects.get(id=recipe.id).time_minutes,
            payload['time_minutes']
        )


class RecipeImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@gotmail.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """Test uploading an image to recipe"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
