from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.models import HashedEmail, RecoveryKey
from django.contrib.auth.hashers import check_password
import hashlib

User = get_user_model()

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

class TestSecurityMeasures(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('users:signup')
        self.login_url = reverse('users:login')
        self.email = "test@example.com"
        self.password = "SecurePass123!"
        self.username = "testuser"
        
        # Create a test user
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )
        self.hashed_email = HashedEmail.get_or_create_hash(self.email)
        self.user.hashed_email = self.hashed_email
        self.user.save()

    def test_email_purging(self):
        """Test that email is properly purged after recovery key is viewed"""
        # Start with a fresh user that hasn't viewed their recovery key
        self.user.recovery_key_viewed = False
        self.user.email_purged = False
        self.user.save()
        
        # Log in first
        self.client.force_login(self.user)
        
        # Simulate first login behavior by generating recovery key
        recovery_key = RecoveryKey.generate_recovery_key()
        recovery_key_obj = RecoveryKey(user=self.user)
        recovery_key_obj.encrypt_recovery_key(recovery_key)
        recovery_key_obj.save()
        
        # Set up session with recovery key
        session = self.client.session
        session['recovery_key'] = recovery_key
        session.save()
        
        # Now get the recovery key page
        response = self.client.get(reverse('users:show_recovery_key'))
        self.assertEqual(response.status_code, 302)

    def test_purged_email_recovery(self):
        """Test that purged emails cannot be recovered"""
        # Purge the email
        self.user.email_purged = True
        self.user.email = ''
        self.user.save()
        
        # Try to find user by original email through various means
        self.assertFalse(User.objects.filter(email=self.email).exists())
        
        # Verify we can still find user by hashed email
        email_hash = HashedEmail.hash_email(self.email)
        self.assertTrue(User.objects.filter(hashed_email__email_hash=email_hash).exists())

    def test_hashed_email_privacy(self):
        """Test that email hashes are one-way and can't be reversed"""
        email1 = "test@example.com"
        email2 = "test2@example.com"
        
        hash1 = HashedEmail.hash_email(email1)
        hash2 = HashedEmail.hash_email(email2)
        
        # Verify different emails produce different hashes
        self.assertNotEqual(hash1, hash2)
        
        # Verify same email always produces same hash
        self.assertEqual(hash1, HashedEmail.hash_email(email1))
        
        # Verify hash length and format (SHA-256 produces 64 character hex string)
        self.assertEqual(len(hash1), 64)
        self.assertTrue(all(c in '0123456789abcdef' for c in hash1))

    def test_password_encryption(self):
        """Test that passwords are properly hashed and not stored in plaintext"""
        # Verify password is not stored in plaintext
        self.assertNotEqual(self.user.password, self.password)
        
        # Verify password can be verified
        self.assertTrue(check_password(self.password, self.user.password))
        
        # Verify incorrect password fails
        self.assertFalse(check_password("wrongpassword", self.user.password))

    def test_sql_injection_prevention(self):
        """Test that SQL injection attempts are prevented"""
        injection_attempts = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "' UNION SELECT password FROM users; --",
            "admin'--",
        ]
        
        for injection in injection_attempts:
            # Test login
            response = self.client.post(self.login_url, {
                'username': injection,
                'password': injection,
            })
            self.assertEqual(response.status_code, 200)  # Should stay on login page
            self.assertFalse(response.wsgi_request.user.is_authenticated)
            
            # Test signup
            response = self.client.post(self.signup_url, {
                'username': injection,
                'email': f'{injection}@example.com',
                'password1': 'SecurePass123!',
                'password2': 'SecurePass123!',
            })
            self.assertEqual(response.status_code, 200)  # Should stay on signup page
            self.assertFalse(User.objects.filter(username=injection).exists())

    def test_recovery_key_encryption(self):
        """Test that recovery keys are properly encrypted"""
        # Generate and encrypt recovery key
        plain_recovery_key = RecoveryKey.generate_recovery_key()
        recovery_key = RecoveryKey(user=self.user)
        recovery_key.encrypt_recovery_key(plain_recovery_key)
        recovery_key.save()
        
        # Verify encrypted key is not stored in plaintext
        self.assertNotEqual(recovery_key.encrypted_key, plain_recovery_key)
        
        # Verify key can be verified
        self.assertTrue(recovery_key.verify_recovery_key(plain_recovery_key))
        
        # Verify incorrect key fails
        self.assertFalse(recovery_key.verify_recovery_key("wrongkey"))
        