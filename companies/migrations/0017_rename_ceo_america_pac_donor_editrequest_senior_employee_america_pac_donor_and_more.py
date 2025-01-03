# Generated by Django 5.1.3 on 2024-11-15 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0016_remove_politicaldata_data_source_datasource'),
    ]

    operations = [
        migrations.RenameField(
            model_name='editrequest',
            old_name='ceo_america_pac_donor',
            new_name='senior_employee_america_pac_donor',
        ),
        migrations.RenameField(
            model_name='editrequest',
            old_name='ceo_save_america_pac_donor',
            new_name='senior_employee_save_america_pac_donor',
        ),
        migrations.RenameField(
            model_name='editrequest',
            old_name='ceo_trump_donor',
            new_name='senior_employee_trump_donor',
        ),
        migrations.RenameField(
            model_name='politicaldata',
            old_name='ceo_america_pac_donor',
            new_name='senior_employee_america_pac_donor',
        ),
        migrations.RenameField(
            model_name='politicaldata',
            old_name='ceo_save_america_pac_donor',
            new_name='senior_employee_save_america_pac_donor',
        ),
        migrations.RenameField(
            model_name='politicaldata',
            old_name='ceo_trump_donor',
            new_name='senior_employee_trump_donor',
        ),
        migrations.AddField(
            model_name='politicaldata',
            name='senior_employee_conservative_total_donations',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='politicaldata',
            name='senior_employee_liberal_total_donations',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='politicaldata',
            name='senior_employee_total_donations',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
    ]
