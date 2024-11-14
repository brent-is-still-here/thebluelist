from django.conf import settings
from django.core.exceptions import ValidationError
from django.middleware.csrf import get_token
from django.test import Client, TestCase
from django.urls import reverse
from users.forms import SignupForm, LoginForm, PasswordResetForm
from users.models import User, HashedEmail


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

    def test_username_validation(self):
        """Test username validation rules"""
        invalid_usernames = [
            '',                    # Empty username
            'a',                   # Too short (if configured)
            'a' * 200,             # Too long (Django's limit is 150)
            'test\x00user',        # Null character
            'test@user@domain',    # Multiple @ symbols
            '\u0000',              # Null unicode character
            'admin\\path',         # Backslash
            'user\tname',          # Tab character
            'admin/test',          # Forward slash
            'test\nuser'           # Newline character
        ]
        
        for username in invalid_usernames:
            data = self.valid_data.copy()
            data['username'] = username
            form = SignupForm(data=data)
            self.assertFalse(
                form.is_valid(),
                f"Username '{username}' should be invalid but was accepted"
            )
            self.assertTrue(
                'username' in form.errors or '__all__' in form.errors,
                f"No error message for invalid username '{username}'"
            )

    def test_password_validation(self):
        """Test password requirements"""
        test_cases = [
            {
                'password': 'short',
                'error': 'This password is too short'
            },
            {
                'password': '12345678',
                'error': 'This password is entirely numeric'
            },
            {
                'password': 'password123',
                'error': 'This password is too common'
            }
        ]
        
        for case in test_cases:
            data = self.valid_data.copy()
            data['password1'] = case['password']
            data['password2'] = case['password']
            form = SignupForm(data=data)
            form.is_valid()  # Trigger validation
            self.assertFalse(form.is_valid())
            self.assertTrue(any(case['error'] in error for error in form.errors.get('password2', [])))

# Add new test classes:
class TestLoginForm(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            email_verified=True
        )
        self.valid_data = {
            'username': 'testuser',
            'password': 'testpass123',
        }

    def test_valid_login(self):
        """Test valid login credentials"""
        form = LoginForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_unverified_email(self):
        """Test login with unverified email"""
        self.user.email_verified = False
        self.user.save()
        
        form = LoginForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Please verify your email', str(form.errors['__all__']))

    def test_remember_me(self):
        """Test remember me functionality"""
        data = self.valid_data.copy()
        data['remember_me'] = True
        form = LoginForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.cleaned_data['remember_me'])

class TestPasswordResetForm(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='OldPass123!'
        )
        self.valid_data = {
            'username': 'testuser',
            'recovery_key': 'valid-recovery-key',
            'new_password1': 'NewPass123!',
            'new_password2': 'NewPass123!'
        }

    def test_password_match(self):
        """Test password matching validation"""
        data = self.valid_data.copy()
        data['new_password2'] = 'DifferentPass123!'
        form = PasswordResetForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("The two password fields didn't match", 
                    str(form.errors['__all__'][0]))

    def test_nonexistent_username(self):
        """Test reset attempt with non-existent username"""
        data = self.valid_data.copy()
        data['username'] = 'nonexistent'
        data['new_password1'] = 'NewPass123!'
        data['new_password2'] = 'NewPass123!'
        form = PasswordResetForm(data=data)
        self.assertTrue(form.is_valid()) 

class TestCSRFProtection(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.signup_url = reverse('users:signup')
        self.login_url = reverse('users:login')
        self.valid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }

    def test_csrf_required(self):
        """Test CSRF protection"""
        response = self.client.post(self.signup_url, self.valid_data)
        self.assertEqual(response.status_code, 403)  # CSRF verification failed

    def test_csrf_token_included(self):
        """Test CSRF token in form rendering"""
        response = self.client.get(self.signup_url)
        self.assertContains(response, 'csrfmiddlewaretoken')