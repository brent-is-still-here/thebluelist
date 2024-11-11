# companies/management/commands/ensure_admin.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Ensures superuser exists with environment variables'

    def handle(self, *args, **options):
        username = os.getenv('DJANGO_SUPERUSER_USERNAME')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD')

        if not all([username, email, password]):
            self.stdout.write(self.style.ERROR('Environment variables for superuser not set properly'))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" already exists'))
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            email_verified=True  # Add this if you're using your custom user model
        )
        self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created successfully'))