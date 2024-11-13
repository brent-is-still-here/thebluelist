from .base import *
import os

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'thebluelist',
        'USER': 'thebluelist_user',
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Override email settings for local development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
MAILTRAP_API_TOKEN = 'dummy-token-for-local'  # Won't be used due to console backend
MAILTRAP_SENDER_EMAIL = 'noreply@mybluelist.org'

# maximum accounts from the same email to avoid spamming
MAX_ACCOUNTS_PER_EMAIL = 2
