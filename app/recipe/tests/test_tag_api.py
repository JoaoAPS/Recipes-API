from django.test import TestCase
from django.contrib.auth import get_user_model
from django.shortcuts import reverse

from rest_framework.test import APIClient
from rest_framework import status

from recipe.models import Tag
from recipe.serializers import TagSerializer


TAG_LIST_URL = reverse('recipe:tag-list')


class PublicTagApiTests(TestCase):
    """Test the API for public requests"""

    def setUp(self):
        self.client = APIClient()

    def test_tag_list_unauthorized(self):
        """Test that access to the tag list is forbiden if unauthorized"""
        res = self.client.get(TAG_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTests(TestCase):
    """Test the API for requests that require authorization"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@gotmail.com',
            password='testpass',
            name='Test Name'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_tag_list_get(self):
        """Test the user can retrive their tags"""
        Tag.objects.create(name="TestTag1", user=self.user)
        Tag.objects.create(name="TestTag2", user=self.user)
        tags = Tag.objects.all().order_by('name')
        serializer = TagSerializer(tags, many=True)

        res = self.client.get(TAG_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_auth_user(self):
        """Test that tags returned are only from the user"""
        user2 = get_user_model().objects.create_user(
            'other@gotmail.com',
            'asdfqwe'
        )
        Tag.objects.create(name="TestTag1", user=self.user)
        Tag.objects.create(name="OtherUserTag", user=user2)

        res = self.client.get(TAG_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], "TestTag1")

    def test_create_tag_successful(self):
        """Test creating a new tag with the api"""
        payload = {'name': 'TestTag'}
        res = self.client.post(TAG_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Tag.objects.filter(
            name=payload['name'],
            user=self.user
        ).exists())

    def test_create_tag_invalid(self):
        """Test creating a new tag with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(TAG_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Tag.objects.filter(
            name=payload['name'],
            user=self.user
        ).exists())

    def test_pass_id_on_create_payload_invalid(self):
        """Test that the tag id cannot be set by the request"""
        payload = {'name': 'TestTag', 'id': 200}
        self.client.post(TAG_LIST_URL, payload)

        self.assertNotEqual(Tag.objects.get(
            name=payload['name'],
            user=self.user
        ).id, payload['id'])
