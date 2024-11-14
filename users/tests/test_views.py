from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from users.models import HashedEmail, User, RecoveryKey
from unittest.mock import patch

User = get_user_model()

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

class TestLoginSystem(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('users:login')
        self.email = "test@example.com"
        self.password = "SecurePass123!"
        self.username = "testuser"
        
        # Create a verified user
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password,
            email_verified=True
        )
        self.hashed_email = HashedEmail.get_or_create_hash(self.email)
        self.user.hashed_email = self.hashed_email
        self.user.save()

    def test_successful_login(self):
        """Test successful login with valid credentials"""
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': self.password,
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after login
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_reject_unverified_email(self):
        """Test that unverified email accounts cannot login"""
        self.user.email_verified = False
        self.user.save()

        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': self.password,
        })
        self.assertEqual(response.status_code, 200)  # Stays on login page
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertFormError(
            response.context['form'],
            None,  # Form-wide error
            "Please verify your email address before logging in."
        )

    def test_reject_incorrect_password(self):
        """Test that incorrect passwords are rejected"""
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertFormError(
            response.context['form'],
            None,  # Form-wide error
            "Please enter a correct username and password. Note that both fields may be case-sensitive."
        )

    def test_remember_me_functionality(self):
        """Test remember me checkbox functionality"""
        # Make sure any existing recovery key is removed
        RecoveryKey.objects.filter(user=self.user).delete()
        
        # Without remember me
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': self.password,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertTrue(response.client.session.get_expire_at_browser_close())

        # Clean up between tests - delete recovery key and logout
        RecoveryKey.objects.filter(user=self.user).delete()
        self.client.logout()

        # With remember me
        self.client.logout()
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': self.password,
            'remember_me': True,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertFalse(response.client.session.get_expire_at_browser_close())

    def test_last_login_update(self):
        """Test that last_login timestamp is updated"""
        old_last_login = self.user.last_login
        
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': self.password,
        })
        
        # Refresh user from database
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.last_login)
        if old_last_login:
            self.assertGreater(self.user.last_login, old_last_login)

    def test_blocked_account_handling(self):
        """Test that blocked accounts cannot login"""
        self.hashed_email.is_blocked = True
        self.hashed_email.save()

        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': self.password,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, "This account has been disabled due to suspicious activity")

    @patch('users.views.email_service.send_verification_email')
    def test_first_time_login_recovery_key(self, mock_send_email):
        """Test recovery key generation on first login"""
        self.user.recovery_key_viewed = False
        self.user.save()
        
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': self.password,
        })
        
        # Should redirect to recovery key page
        self.assertRedirects(response, reverse('users:show_recovery_key'))
        
        # Verify recovery key was generated
        self.assertTrue(RecoveryKey.objects.filter(user=self.user).exists())
        
        # Verify recovery key is in session
        self.assertIn('recovery_key', self.client.session)

    def test_subsequent_login_no_recovery_key(self):
        """Test that subsequent logins don't generate new recovery keys"""
        self.user.recovery_key_viewed = True
        self.user.save()
        
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': self.password,
        })
        
        # Should redirect to home
        self.assertRedirects(response, reverse('home'))
        
        # Verify no recovery key in session
        self.assertNotIn('recovery_key', self.client.session)