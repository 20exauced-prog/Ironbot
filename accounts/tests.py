from django.test import TestCase
from django.urls import reverse

from .models import CustomUser


class SignUpViewTests(TestCase):
    def test_signup_page_is_available(self):
        response = self.client.get(reverse('signup'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Active ton acces Ironbot")

    def test_signup_creates_user_and_logs_them_in(self):
        response = self.client.post(
            reverse('signup'),
            {
                'username': 'charlie',
                'email': 'charlie@example.com',
                'phone_number': '+22900000000',
                'password1': 'UnMotDePasseSolide123',
                'password2': 'UnMotDePasseSolide123',
            },
        )

        self.assertRedirects(response, reverse('my_licenses'))
        self.assertTrue(CustomUser.objects.filter(username='charlie').exists())
        self.assertEqual(int(self.client.session['_auth_user_id']), CustomUser.objects.get(username='charlie').pk)

    def test_signup_rejects_duplicate_email(self):
        CustomUser.objects.create_user(username='alice', email='alice@example.com', password='secret123')

        response = self.client.post(
            reverse('signup'),
            {
                'username': 'charlie',
                'email': 'alice@example.com',
                'phone_number': '+22900000000',
                'password1': 'UnMotDePasseSolide123',
                'password2': 'UnMotDePasseSolide123',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cette adresse email est deja utilisee.")


class LoginSecurityTests(TestCase):
    def test_login_page_is_available(self):
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Entre dans le cockpit Ironbot")

    def test_login_is_rate_limited_after_many_failures(self):
        for _ in range(7):
            response = self.client.post(reverse('login'), {'username': 'nobody', 'password': 'wrong-pass'})
            self.assertEqual(response.status_code, 200)

        blocked = self.client.post(reverse('login'), {'username': 'nobody', 'password': 'wrong-pass'})

        self.assertEqual(blocked.status_code, 403)
