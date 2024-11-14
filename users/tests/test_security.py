from django.test import Client, TestCase
from django.urls import reverse

class TestRegistrationSecurity(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('users:signup')

    def test_sql_injection_username(self):
        data = {
            'username': "'; DROP TABLE users;--",
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'],
            'username', 
            'Enter a valid username. This value may contain only letters, '
            'numbers, and @/./+/-/_ characters.'
        )

    def test_sql_injection_email(self):
        data = {
            'username': 'testuser',
            'email': "'; DROP TABLE users;--@example.com",
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'],
            'email',
            'Enter a valid email address.'
        )

    def test_xss_username(self):
        data = {
            'username': '<script>alert("xss")</script>',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'],
            'username',
            'Enter a valid username. This value may contain only letters, '
            'numbers, and @/./+/-/_ characters.'
        )