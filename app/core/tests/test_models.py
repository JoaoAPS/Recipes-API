from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Tests creating a use with an email successfully"""
        email = "test123@hotmail.com"
        password = "LePass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEquals(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = "TeSt123@HotMAIL.com"
        user = get_user_model().objects.create_user(email, 'testpass')

        self.assertEquals(user.email, "TeSt123@hotmail.com")

    def test_new_user_invalid(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_superuser(self):
        """Test creating new super user"""
        user = get_user_model().objects.create_superuser(
            'test@hotmail.com',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
