from datetime import timedelta
from django.test import Client, TestCase, override_settings
from django.core.exceptions import ValidationError
from users.models import User, HashedEmail
from django.conf import settings
from django.db import IntegrityError
from django.db.models import Count
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

class TestHashedEmail(TestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.alternate_email = "test+alternate@example.com"
        self.password = "testpass123"

    def test_email_hash_consistency(self):
        """Test that the same email always produces the same hash"""
        # Test basic hash consistency
        hash1 = HashedEmail.hash_email(self.email)
        hash2 = HashedEmail.hash_email(self.email)
        self.assertEqual(hash1, hash2)
        
        # Test case insensitivity
        upper_hash = HashedEmail.hash_email(self.email.upper())
        self.assertEqual(hash1, upper_hash)
        
        # Test whitespace handling
        spaced_hash = HashedEmail.hash_email(f" {self.email} ")
        self.assertEqual(hash1, spaced_hash)
        
        # Test different emails produce different hashes
        different_hash = HashedEmail.hash_email("different@example.com")
        self.assertNotEqual(hash1, different_hash)

    def test_get_or_create_hash(self):
        """Test the get_or_create_hash functionality"""
        # First creation
        hashed_email1 = HashedEmail.get_or_create_hash(self.email)
        self.assertIsNotNone(hashed_email1)
        self.assertEqual(hashed_email1.email_hash, HashedEmail.hash_email(self.email))
        
        # Getting existing hash
        hashed_email2 = HashedEmail.get_or_create_hash(self.email)
        self.assertEqual(hashed_email1, hashed_email2)
        
        # Verify last_used is updated
        old_last_used = hashed_email1.last_used
        hashed_email3 = HashedEmail.get_or_create_hash(self.email)
        hashed_email3.refresh_from_db()
        self.assertGreater(hashed_email3.last_used, old_last_used)

    def test_active_users_counting(self):
        """Test counting of active users"""
        hashed_email = HashedEmail.get_or_create_hash(self.email)
        
        # Create users with different last_login times
        now = timezone.now()
        
        # Active user (logged in recently)
        active_user = User.objects.create_user(
            username="active",
            email=self.email,
            password=self.password
        )
        active_user.last_login = now - timedelta(days=15)
        active_user.hashed_email = hashed_email
        active_user.save()
        
        # Inactive user (logged in long ago)
        inactive_user = User.objects.create_user(
            username="inactive",
            email=self.email,
            password=self.password
        )
        inactive_user.last_login = now - timedelta(days=45)
        inactive_user.hashed_email = hashed_email
        inactive_user.save()
        
        # Test 30-day active user count
        self.assertEqual(hashed_email.get_active_users_count(days=30), 1)
        
        # Test with different day ranges
        self.assertEqual(hashed_email.get_active_users_count(days=10), 0)
        self.assertEqual(hashed_email.get_active_users_count(days=60), 2)

    def test_total_users_counting(self):
        """Test counting total users"""
        hashed_email = HashedEmail.get_or_create_hash(self.email)
        
        # Create multiple users with the same hashed email
        for i in range(3):
            user = User.objects.create_user(
                username=f"user{i}",
                email=self.email,
                password=self.password
            )
            user.hashed_email = hashed_email
            user.save()
        
        self.assertEqual(hashed_email.get_total_users_count(), 3)
        
        # Test count updates when adding/removing users
        user4 = User.objects.create_user(
            username="user4",
            email=self.email,
            password=self.password
        )
        user4.hashed_email = hashed_email
        user4.save()
        
        self.assertEqual(hashed_email.get_total_users_count(), 4)
        
        user4.delete()
        self.assertEqual(hashed_email.get_total_users_count(), 3)

    def test_blocking_functionality(self):
        """Test email blocking functionality"""
        hashed_email = HashedEmail.get_or_create_hash(self.email)
        
        # Test initial state
        self.assertFalse(hashed_email.is_blocked)
        
        # Test blocking
        hashed_email.is_blocked = True
        hashed_email.save()
        
        # Verify block persists after refresh
        hashed_email.refresh_from_db()
        self.assertTrue(hashed_email.is_blocked)
        
        # Test that blocked email hash still works with get_or_create
        blocked_hash = HashedEmail.get_or_create_hash(self.email)
        self.assertTrue(blocked_hash.is_blocked)
        
        # Verify we can unblock
        hashed_email.is_blocked = False
        hashed_email.save()
        hashed_email.refresh_from_db()
        self.assertFalse(hashed_email.is_blocked)

    def test_hash_uniqueness(self):
        """Test that email hash is unique"""
        from django.db import transaction
        
        # First create a hashed email
        hashed_email1 = HashedEmail.get_or_create_hash(self.email)
        
        # Try to create duplicate hash directly - this should fail
        with transaction.atomic():
            try:
                HashedEmail.objects.create(
                    email_hash=HashedEmail.hash_email(self.email)
                )
                self.fail("Should have raised IntegrityError")
            except IntegrityError:
                # This is expected
                pass
        
        # Verify get_or_create_hash returns existing hash
        hashed_email2 = HashedEmail.get_or_create_hash(self.email)
        self.assertEqual(hashed_email1.id, hashed_email2.id)
        self.assertEqual(hashed_email1.email_hash, hashed_email2.email_hash)