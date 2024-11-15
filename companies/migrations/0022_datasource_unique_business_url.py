# Generated by Django 5.1.3 on 2024-11-15 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0021_datasource_edit_request_datasource_is_approved'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='datasource',
            constraint=models.UniqueConstraint(fields=('business', 'url'), name='unique_business_url'),
        ),
    ]
