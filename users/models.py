
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True)
