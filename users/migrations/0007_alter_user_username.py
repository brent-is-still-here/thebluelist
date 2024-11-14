# Generated by Django 5.1.3 on 2024-11-14 15:22

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_user_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(error_messages={'invalid': 'Username may only contain letters, numbers, underscores, and hyphens.', 'max_length': 'Username cannot be longer than 32 characters.', 'min_length': 'Username must be at least 3 characters long.', 'unique': 'A user with that username already exists.'}, help_text='Required. 3-32 characters. Letters, numbers, underscores, and hyphens only.', max_length=32, unique=True, validators=[django.core.validators.MinLengthValidator(3), django.core.validators.RegexValidator(message='Username may only contain letters, numbers, underscores, and hyphens.', regex='^[a-zA-Z0-9_-]+$')]),
        ),
    ]
