from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token


User = get_user_model()


class AuthTests(APITestCase):
    def test_user_registration_creates_user_with_telegram_chat_id(self):
        url = "/api/auth/register/"
        data = {
            "email": "test@example.com",
            "password": "strongpass123",
            "username": "testuser",
            "phone_number": "+70000000000",
            "first_name": "Test",
            "last_name": "User",
            "telegram_chat_id": "123456789",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="test@example.com").exists())

        user = User.objects.get(email="test@example.com")
        self.assertNotEqual(user.password, data["password"])
        self.assertTrue(user.check_password(data["password"]))
        self.assertEqual(user.telegram_chat_id, "123456789")

    def test_login_returns_token_for_valid_credentials(self):
        user = User.objects.create_user(
            email="test2@example.com",
            password="strongpass123",
            username="testuser2",
        )

        url = "/api/auth/login/"
        data = {"username": "test2@example.com", "password": "strongpass123"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

        token_value = response.data["token"]
        token = Token.objects.get(user=user)
        self.assertEqual(token.key, token_value)
