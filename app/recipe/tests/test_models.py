from django.test import TestCase
from django.contrib.auth import get_user_model
from recipe.models import Tag, Ingredient, Recipe


def sample_user(email='test@gotmail.com', password='testpass', name='Name'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password, name=name)


def sample_tag(user, name='TestTag'):
    """Create a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='TestIngredient'):
    """Create a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


class ModelTest(TestCase):

    def test_create_retrieve_tag(self):
        """Test creating a tag and retrieving its string representation"""
        tag = Tag.objects.create(name="TestTag", user=sample_user())
        self.assertEqual(str(tag), "TestTag")

    def test_create_retrieve_ingredient(self):
        """Test ingredient creation and string representation"""
        ingredient = Ingredient.objects.create(
            name="Test Ingridient",
            user=sample_user()
        )
        self.assertEqual(str(ingredient), "Test Ingridient")

    def test_create_recipe(self):
        """Test creating a recipe"""
        recipe = Recipe.objects.create(
            user=sample_user(),
            title="Test Recipe",
            time_minutes=5,
            price=5.00
        )

        self.assertEqual(str(recipe), recipe.title)
