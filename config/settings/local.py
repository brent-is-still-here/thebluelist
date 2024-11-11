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

# Email settings (example with MailChimp)
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
MAILTRAP_API_TOKEN = os.environ.get('MAILTRAP_API_TOKEN')
MAILTRAP_SENDER_EMAIL = 'noreply@mybluelist.org'
