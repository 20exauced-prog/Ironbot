from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import CustomUser
from licenses.models import License


class MyLicensesViewTests(TestCase):
    def setUp(self):
        self.owner = CustomUser.objects.create_user(username="alice", password="secret123")
        self.other_user = CustomUser.objects.create_user(username="bob", password="secret123")

    def test_redirects_anonymous_users_to_login(self):
        response = self.client.get(reverse("my_licenses"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_shows_only_current_users_licenses(self):
        visible_license = License.objects.create(
            user=self.owner,
            key="VISIBLE-123",
            expires_at=timezone.now() + timedelta(days=30),
        )
        License.objects.create(
            user=self.other_user,
            key="HIDDEN-456",
            expires_at=timezone.now() + timedelta(days=30),
        )

        self.client.login(username="alice", password="secret123")
        response = self.client.get(reverse("my_licenses"))

        licenses = list(response.context["licenses"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(licenses, [visible_license])
        self.assertContains(response, "VISIBLE-123")
        self.assertNotContains(response, "HIDDEN-456")
