from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.test import TestCase

from .models import UserProfile
User = get_user_model()


# class RegisterPasswordValidationTests(APITestCase):
#     def test_register_rejects_weak_password(self):
#         response = self.client.post(
#             reverse("register"),
#             {
#                 "username": "weakuser",
#                 "email": "weak@example.com",
#                 "password": "weak1234",
#                 "confirm_password": "weak1234",
#             },
#             format="json",
#         )

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("password", response.data)

#     def test_register_accepts_strong_password(self):
#         response = self.client.post(
#             reverse("register"),
#             {
#                 "username": "stronguser",
#                 "email": "strong@example.com",
#                 "password": "Strong@123",
#                 "confirm_password": "Strong@123",
#             },
#             format="json",
#         )

#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertTrue(User.objects.filter(username="stronguser").exists())
        
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
        
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import UserProfile

User = get_user_model()


class RegistrationRoleTests(APITestCase):
    def test_new_user_gets_analyst_role(self):
        response = self.client.post(
            "/api/v1/auth/register/",
            {
                "username": "newuser",
                "email": "new@example.com",
                "password": "Strong@123",
                "confirm_password": "Strong@123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(username="newuser")

        self.assertTrue(
            UserProfile.objects.filter(
                user=user,
                role=UserProfile.Role.ANALYST,
            ).exists()
        )

    def test_public_registration_cannot_select_admin_role(self):
        response = self.client.post(
            "/api/v1/auth/register/",
            {
                "username": "attacker",
                "email": "attacker@example.com",
                "password": "Strong@123",
                "confirm_password": "Strong@123",
                "role": "company_admin",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(username="attacker")

        self.assertEqual(
            user.profile.role,
            UserProfile.Role.ANALYST,
        )

    def test_registration_does_not_seed_demo_sales(self):
        from sales.models import SalesTransaction

        self.assertEqual(SalesTransaction.objects.count(), 0)

        response = self.client.post(
            "/api/v1/auth/register/",
            {
                "username": "cleanuser",
                "email": "clean@example.com",
                "password": "Strong@123",
                "confirm_password": "Strong@123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SalesTransaction.objects.count(), 0)
        
class CurrentUserRoleTests(APITestCase):
    def test_current_user_returns_role(self):
        user = User.objects.create_user(
            username="roleuser",
            email="role@example.com",
            password="Strong@123",
        )

        UserProfile.objects.create(
            user=user,
            role=UserProfile.Role.SALES_MANAGER,
        )

        self.client.force_authenticate(user=user)

        response = self.client.get(reverse("current-user"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["role"], UserProfile.Role.SALES_MANAGER)