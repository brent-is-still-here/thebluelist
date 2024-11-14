from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.middleware import EmailVerificationMiddleware
from django.http import HttpResponse
from users.models import HashedEmail
from django.contrib.messages import get_messages

User = get_user_model()

class TestEmailVerificationMiddleware(TestCase):
    def setUp(self):
        self.client = Client()
        self.email = "test@example.com"
        self.password = "testpass123"
        
        # Create an unverified user
        self.unverified_user = User.objects.create_user(
            username="unverified",
            email=self.email,
            password=self.password,
            email_verified=False
        )
        
        # Create a verified user
        self.verified_user = User.objects.create_user(
            username="verified",
            email="verified@example.com",
            password=self.password,
            email_verified=True
        )
        
        # Create a superuser
        self.superuser = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password=self.password,
            email_verified=False  # Even unverified should work for superuser
        )

    def test_unverified_user_access(self):
        """Test that unverified users are redirected appropriately"""
        self.client.force_login(self.unverified_user)
        
        # Try accessing home page
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('users:verification_sent'))
        
        # Check warning message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any('Please verify your email' in str(m) for m in messages)
        )

    def test_verified_user_access(self):
        """Test that verified users can access pages"""
        self.client.force_login(self.verified_user)
        
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_superuser_bypass(self):
        """Test that superusers bypass verification requirement"""
        self.client.force_login(self.superuser)
        
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_allowed_paths(self):
        """Test access to allowed paths for unverified users"""
        self.client.force_login(self.unverified_user)
        
        # Test verification sent page
        response = self.client.get(reverse('users:verification_sent'))
        self.assertEqual(response.status_code, 200)
        
        # Test resend verification
        response = self.client.post(reverse('users:resend_verification'))
        self.assertRedirects(response, reverse('users:verification_sent'))
        
        # Test logout
        response = self.client.post(reverse('users:logout'))
        self.assertRedirects(response, reverse('home'))

    def test_unauthenticated_access(self):
        """Test that unauthenticated users aren't affected by middleware"""
        # Should be able to access login page
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
        
        # Should be able to access signup page
        response = self.client.get(reverse('users:signup'))
        self.assertEqual(response.status_code, 200)

    def test_verification_state_change(self):
        """Test behavior when user's verification state changes"""
        self.client.force_login(self.unverified_user)
        
        # Initially should be redirected
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('users:verification_sent'))
        
        # Verify the user
        self.unverified_user.email_verified = True
        self.unverified_user.save()
        
        # Should now have access
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)