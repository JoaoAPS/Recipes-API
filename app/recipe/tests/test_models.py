from django.test import TestCase
from django.contrib.auth import get_user_model
from recipe.models import Tag


def sample_user(email='test@gotmail.com', password='testpass', name='Name'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password, name=name)


class ModelTest(TestCase):

    def test_create_retrieve_tag(self):
        """Test creating a tag and retrieving its string representation"""
        tag = Tag.objects.create(name="TestTag", user=sample_user())
        self.assertEqual(str(tag), "TestTag")
