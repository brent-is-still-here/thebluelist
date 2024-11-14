from django.urls import reverse
from django.core import mail
from django.test import Client, TestCase, override_settings
from users.models import User
from unittest.mock import patch

@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
)

class TestSignupView(TestCase):
    def setUp(self):
        self.valid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        self.signup_url = reverse('users:signup')

    @patch('users.views.email_service.send_verification_email')
    def test_signup_success(self, mock_send_email):
        # Configure the mock to return success
        mock_send_email.return_value = (True, "mock_message_id")
        
        response = self.client.post(self.signup_url, self.valid_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users:verification_sent'))
        
        # Verify user was created
        user = User.objects.get(username=self.valid_data['username'])
        self.assertFalse(user.email_verified)
        self.assertTrue(user.verification_token)
        
        # Verify email service was called
        mock_send_email.assert_called_once()

    def test_signup_duplicate_username(self):
        # Create user first
        User.objects.create_user(
            username=self.valid_data['username'],
            email='other@example.com',
            password='testpass123'
        )
        
        # Try to create duplicate
        response = self.client.post(self.signup_url, self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'username',
            'A user with that username already exists.'
        )

    def test_signup_invalid_email(self):
        self.valid_data['email'] = 'invalid-email'
        response = self.client.post(self.signup_url, self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'email',
            'Enter a valid email address.'
        )
