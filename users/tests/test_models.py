import pytest
from django.test import Client, TestCase, override_settings
from django.core.exceptions import ValidationError
from users.models import User, HashedEmail
from django.conf import settings
from django.utils import timezone

@override_settings(MAX_ACCOUNTS_PER_EMAIL=2)
class TestUserRegistration(TestCase):
    def setUp(self):
        self.valid_email = "test@example.com"
        self.valid_username = "testuser"
        self.valid_password = "testpass123"

    def test_create_user_success(self):
        user = User.objects.create_user(
            username=self.valid_username,
            email=self.valid_email,
            password=self.valid_password
        )
        self.assertFalse(user.email_verified)
        self.assertFalse(user.recovery_key_viewed)
        self.assertFalse(user.email_purged)
        self.assertIsNone(user.last_login)

    def test_create_user_with_duplicate_email(self):
        # First create a user with the email
        user1 = User.objects.create_user(
            username="user1",
            email=self.valid_email,
            password=self.valid_password
        )
        # Explicitly create and assign HashedEmail
        hashed_email = HashedEmail.get_or_create_hash(self.valid_email)
        user1.hashed_email = hashed_email
        user1.save()
        
        # Create second user
        user2 = User.objects.create_user(
            username="user2",
            email=self.valid_email,
            password=self.valid_password
        )
        user2.hashed_email = hashed_email
        user2.save()
        
        # Verify both users are linked to the same HashedEmail
        self.assertEqual(
            User.objects.filter(hashed_email=hashed_email).count(),
            2
        )

    def test_hashed_email_creation(self):
        hashed_email = HashedEmail.get_or_create_hash(self.valid_email)
        self.assertIsNotNone(hashed_email)
        self.assertEqual(
            hashed_email.email_hash,
            HashedEmail.hash_email(self.valid_email)
        )

    def test_max_accounts_per_email(self):
        hashed_email = HashedEmail.get_or_create_hash(self.valid_email)
        
        # Create maximum allowed accounts
        for i in range(settings.MAX_ACCOUNTS_PER_EMAIL):
            user = User.objects.create_user(
                username=f"user{i}",
                email=self.valid_email,
                password=self.valid_password
            )
            user.hashed_email = hashed_email
            user.save()
        
        # Verify count
        self.assertEqual(
            User.objects.filter(hashed_email=hashed_email).count(),
            settings.MAX_ACCOUNTS_PER_EMAIL
        )
