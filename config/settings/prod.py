import os
import dj_database_url
from .base import *

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        }
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'companies': {  
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'users': {  
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        }
    }
}

DEBUG = False
ALLOWED_HOSTS = ['.railway.app', 'mybluelist.org', 'www.mybluelist.org']

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

print(f"Database settings: {os.environ.get('PGDATABASE')}, {os.environ.get('PGHOST')}")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('PGDATABASE'),
        'USER': os.environ.get('PGUSER'),
        'PASSWORD': os.environ.get('PGPASSWORD'),
        'HOST': os.environ.get('PGHOST'),
        'PORT': os.environ.get('PGPORT', '5432'),
    }
}

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Static files
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
MAILTRAP_API_TOKEN = os.environ.get('MAILTRAP_API_TOKEN')
MAILTRAP_SENDER_EMAIL = 'noreply@mybluelist.org'

# maximum accounts from the same email to avoid spamming
MAX_ACCOUNTS_PER_EMAIL = 5
