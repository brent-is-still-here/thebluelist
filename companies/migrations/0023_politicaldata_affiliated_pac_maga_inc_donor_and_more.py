# Generated by Django 5.1.3 on 2024-11-15 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0022_datasource_unique_business_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='politicaldata',
            name='affiliated_pac_maga_inc_donor',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='politicaldata',
            name='direct_maga_inc_donor',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='politicaldata',
            name='senior_employee_maga_inc_donor',
            field=models.BooleanField(default=False),
        ),
    ]