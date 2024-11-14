from django.conf import settings
from django.test import Client, TestCase
from users.models import User, HashedEmail
from users.forms import SignupForm

class TestSignupForm(TestCase):
    def setUp(self):
        self.valid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }

    def test_valid_signup_form(self):
        form = SignupForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_invalid_email_format(self):
        self.valid_data['email'] = 'invalid-email'
        form = SignupForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_duplicate_email(self):
        # Create a user first
        User.objects.create_user(
            username='existinguser',
            email=self.valid_data['email'],
            password='testpass123'
        )
        
        # Try to create another user with same email
        form = SignupForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_blocked_email_hash(self):
        # Create and block a hashed email
        hashed_email = HashedEmail.get_or_create_hash(self.valid_data['email'])
        hashed_email.is_blocked = True
        hashed_email.save()
        
        form = SignupForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_max_accounts_reached(self):
        email = self.valid_data['email']
        hashed_email = HashedEmail.get_or_create_hash(email)
        
        # Create maximum allowed accounts
        for i in range(settings.MAX_ACCOUNTS_PER_EMAIL):
            User.objects.create_user(
                username=f"user{i}",
                email=email,
                password='testpass123'
            )
        
        # Try to create one more account
        form = SignupForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
