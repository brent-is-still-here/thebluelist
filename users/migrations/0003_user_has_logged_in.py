# Generated by Django 5.1.3 on 2024-11-13 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_email_purged_user_recovery_key_viewed_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='has_logged_in',
            field=models.BooleanField(default=False),
        ),
    ]