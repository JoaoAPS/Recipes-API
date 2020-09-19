from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUsersApiTest(TestCase):
    """Test the user API for public requests"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'mybestpass',
            'name': 'Test name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creating a user that already exists fail"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'mybestpass',
            'name': 'Test name'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 characters"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'qwtw',
            'name': 'Test name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'mybestpass',
            'name': 'Test name'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_create_token_invalid_credentials(self):
        """Test that token in not created if invalid credintials are given"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'mybestpass',
            'name': 'Test name'
        }
        create_user(email=payload['email'], password='wrongpass')
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user does not exists"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'mybestpass',
            'name': 'Test name'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        payload = {
            'email': 'test@gmail.com',
            'password': '',
            'name': 'Test name'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        payload = {
            'email': '',
            'password': 'mybestpass',
            'name': 'Test name'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrive_user_unauthorized(self):
        """Test that authentication is required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUsersApiTest(TestCase):
    """Test the user API that require set-ups"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@gotmail.com',
            password='huehuehue',
            name='Test Hue'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_me_get(self):
        """Test that the user recives profile page successuflly"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': self.user.email,
            'name': self.user.name,
        })

    def test_me_put(self):
        """Test that the user can update itself via put request"""
        payload = {
            'email': 'test@gotmail.com',
            'password': 'newpassword',
            'name': 'New Name'
        }
        res = self.client.put(ME_URL, payload)
        self.user.refresh_from_db()
        # updated_user = get_user_model().objects.get(id=self.user.id)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.email, payload['email'])
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))

    def test_me_patch(self):
        """Test that the user can update itself via patch request"""
        payload = {
            'password': 'newpassword',
            'name': 'New Name'
        }
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        # updated_user = get_user_model().objects.get(id=self.user.id)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))

    def test_me_no_post_allowed(self):
        """Test that no post requests are allowed on profile page"""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
