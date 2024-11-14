from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'github_actions',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Test-specific settings
DEBUG = False
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable any expensive/unnecessary settings during testing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]