from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.utils import timezone
from cryptography.fernet import Fernet
from django.conf import settings
import base64
import hashlib
import re
import secrets

def validate_username_characters(value):
    """Custom validator to ensure username only contains allowed characters"""
    if not re.match(r'^[a-zA-Z0-9_-]+$', value):
        raise ValidationError(
            'Username may only contain letters, numbers, underscores, and hyphens.'
        )

class HashedEmail(models.Model):
    """
    Stores hashed email addresses to prevent abuse while maintaining privacy
    """
    email_hash = models.CharField(max_length=64, unique=True)
    first_used = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(auto_now_add=True)
    is_blocked = models.BooleanField(default=False)
    
    @staticmethod
    def hash_email(email):
        """
        Create a consistent hash for an email address
        """
        # Normalize email by lowercasing
        normalized_email = email.lower().strip()
        # Create SHA-256 hash
        return hashlib.sha256(normalized_email.encode()).hexdigest()
    
    @staticmethod
    def get_or_create_hash(email):
        """
        Get or create a HashedEmail instance for the given email
        """
        email_hash = HashedEmail.hash_email(email)
        hashed_email, created = HashedEmail.objects.get_or_create(
            email_hash=email_hash,
            defaults={'last_used': timezone.now()}
        )
        if not created:
            hashed_email.last_used = timezone.now()
            hashed_email.save()
        return hashed_email
    
    def get_active_users_count(self, days=30):
        """
        Get count of associated users active in the last N days
        """
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.users.filter(last_login__gte=cutoff).count()
    
    def get_total_users_count(self):
        """
        Get total count of associated users
        """
        return self.users.count()

class User(AbstractUser):
    username = models.CharField(
        max_length=32,
        unique=True,
        validators=[
            MinLengthValidator(3),
            RegexValidator(
                regex=r'^[a-zA-Z0-9_-]+$',
                message='Username may only contain letters, numbers, underscores, and hyphens.'
            )
        ],
        error_messages={
            'unique': 'A user with that username already exists.',
            'min_length': 'Username must be at least 3 characters long.',
            'max_length': 'Username cannot be longer than 32 characters.',
            'invalid': 'Username may only contain letters, numbers, underscores, and hyphens.'
        },
        help_text='Required. 3-32 characters. Letters, numbers, underscores, and hyphens only.'
    )

    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True)
    email_purged = models.BooleanField(default=False)
    recovery_key_viewed = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    hashed_email = models.ForeignKey(
        HashedEmail,
        on_delete=models.SET_NULL,
        null=True,
        related_name='users'
    )

    def update_last_login(self):
        """
        Update the last login timestamp
        """
        self.last_login = timezone.now()
        self.save(update_fields=['last_login'])

class RecoveryKey(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    encrypted_key = models.CharField(max_length=344)
    key_salt = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_recovery_key():
        """Generate a human-readable recovery key"""
        # Generate 20 bytes of randomness and encode as base32
        return base64.b32encode(secrets.token_bytes(20)).decode('ascii')

    @staticmethod
    def get_encryption_key():
        if not hasattr(settings, 'RECOVERY_KEY_ENCRYPTION_KEY'):
            key = Fernet.generate_key()
            with open('recovery_key.key', 'wb') as key_file:
                key_file.write(key)
        else:
            key = settings.RECOVERY_KEY_ENCRYPTION_KEY
        return Fernet(key)

    def encrypt_recovery_key(self, recovery_key):
        f = self.get_encryption_key()
        self.key_salt = secrets.token_hex(16)
        salted_key = f"{recovery_key}{self.key_salt}"
        encrypted = f.encrypt(salted_key.encode())
        self.encrypted_key = base64.b64encode(encrypted).decode()

    def verify_recovery_key(self, provided_key):
        f = self.get_encryption_key()
        try:
            decrypted = f.decrypt(base64.b64decode(self.encrypted_key))
            stored_key_with_salt = decrypted.decode()
            stored_key = stored_key_with_salt[:-len(self.key_salt)]
            return secrets.compare_digest(provided_key, stored_key)
        except Exception:
            return False