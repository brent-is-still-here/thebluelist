# Generated by Django 5.1.3 on 2024-11-11 17:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0008_alter_business_locations'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productcategory',
            old_name='description',
            new_name='parent',
        ),
        migrations.RenameField(
            model_name='servicecategory',
            old_name='description',
            new_name='parent',
        ),
    ]