from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.test import TestCase

from .models import UserProfile
User = get_user_model()


class RegisterPasswordValidationTests(APITestCase):
    def test_register_rejects_weak_password(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "weakuser",
                "email": "weak@example.com",
                "password": "weak1234",
                "confirm_password": "weak1234",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_register_accepts_strong_password(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "stronguser",
                "email": "strong@example.com",
                "password": "Strong@123",
                "confirm_password": "Strong@123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="stronguser").exists())
        
class UserProfileTests(TestCase):
    def test_user_profile_defaults_to_analyst(self):
        user = get_user_model().objects.create_user(
            username="analyst_user",
            password="Strong@123",
        )

        profile = UserProfile.objects.create(user=user)

        self.assertEqual(
            profile.role,
            UserProfile.Role.ANALYST,
        )

    def test_user_profile_supports_company_admin_role(self):
        user = get_user_model().objects.create_user(
            username="admin_user",
            password="Strong@123",
        )

        profile = UserProfile.objects.create(
            user=user,
            role=UserProfile.Role.COMPANY_ADMIN,
        )

        self.assertEqual(
            profile.get_role_display(),
            "Company Admin",
        )